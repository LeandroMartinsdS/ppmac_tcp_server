import os
import socket
import struct
import time
import logging
import pandas as pd

# Define the server address and port
HOST = '127.0.0.1'  # Replace with your MCU's IP address
PORT = 8080

DATA_FORMAT = '<iidddddddd'  # Format for 6 double variables - forces little-endian
HEADER = None
SEND_RATE_HZ = 2000  # Sending rate in Hz
SHUTDOWN_CMD = "SHUTDOWN"
READY_CMD_PREFIX = "BUFFER_READY:"

# Configure logging to print to the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def pack_row(row, dtype):
    data = row.to_numpy(dtype)  # Convert pandas Series
    # to numpy array of floats
    return struct.pack(DATA_FORMAT, *data)  # Convert to binary


def infer_and_pack_row(row, format_string):
    # Parse the format string to determine types
    format_types = []
    endianness_chars = {'<', '>', '!', '=', '@'}

    i = 0
    while i < len(format_string):
        if format_string[i] in endianness_chars:
            i += 1
            continue
        if format_string[i].isdigit():
            count = int(format_string[i])
            i += 1
            while format_string[i].isdigit():
                count = count * 10 + int(format_string[i])
                i += 1
            format_types.extend([format_string[i]] * count)
        else:
            format_types.append(format_string[i])
        i += 1

    # Cast values to appropriate types based on format string
    casted_data = []
    for value, fmt in zip(row, format_types):
        if fmt in ['i', 'l', 'q', 'h', 'b']:
            casted_data.append(int(value))
        elif fmt in ['f', 'd']:
            casted_data.append(float(value))
        else:
            raise ValueError(f"Unsupported format type: {fmt}")

    # Pack the data into binary format
    return struct.pack(format_string, *casted_data)


def pack_file(df, dtype=DATA_FORMAT):
    packed_data_list = []
    for i, row in df.iterrows():
        # Processing row
        try:
            if row.isnull().all():
                # Skip empty rows
                continue
            packed_data_list.append(infer_and_pack_row(row, dtype))
        except ValueError as e:
            logging.error(f"Error converting row {i} to floats: {e}")
    return packed_data_list


def send_packed_data(sock, packed_data_array, rate_hz,
                     buffer_labels=['A', 'B']):
    interval_ns = 1e9 / rate_hz  # Calculate interval between sends
    tolerance_ns = interval_ns*0.70

    for i, packed_data in enumerate(packed_data_array):

        # expected_slot = buffer_labels[i % len(buffer_labels)] # TODO this is wrong
        # print(f"expected_slot: {expected_slot}")

        # # Wait for the correct buffer to be ready
        # while True:
        #     try:
        #         response = sock.recv(1024).decode().strip()
        #         if response == f"{READY_CMD_PREFIX}{expected_slot}":
        #             logging.info(f"Buffer {expected_slot} is ready on Server")
        #             break

        #     except Exception as e:
        #         logging.error(f"Error receiving buffer ready message: {e}")
        #         return

        # logging.info(f"Interval of {interval_ns} ns") # Log the send duration
        next_send_time = time.perf_counter_ns()  # Initialize the next send time

        try:
            sock.sendall(packed_data)  # Send binary data
            next_send_time += interval_ns  # Update the next send time

            while time.perf_counter_ns() - next_send_time < 1:
                pass

            time_behind = time.perf_counter_ns() - next_send_time
            if (time_behind > tolerance_ns):
                logging.warning(
                    f"Warning: Sending is behind schedule by {time_behind} ns")
                # break

        except Exception as e:
            logging.error(f"Error sending data for buffer at point {i}: {e}")
            return


def list_csv_files(directory, prefix=""):
    try:
        print(f"Checking if directory '{directory}' exists...")
        if not os.path.exists(directory):
            print(f"Directory '{directory}' does not exist.")
            return []

        all_files = os.listdir(directory)

        if not all_files:
            print(f"No files found in directory '{directory}'.")
            return []

        csv_files = [f for f in all_files if f.endswith('.csv') and
                     f.startswith(prefix)]

        if not csv_files:
            logging.info(f"No matching CSV files found in '{directory}'.")

        return csv_files
    except PermissionError:
        print(f"Permission denied for directory '{directory}'.")
        return []


def main():
    dirname = "files"
    filename_prefix = "test"  # Set to "" to include all files
    path = os.path.join(os.path.dirname(__file__), dirname)

    filename_list = list_csv_files(path, filename_prefix)
    file_path_list = [os.path.join(path, filename)
                      for filename in filename_list]

    print(f"CSV files in '{path}':")
    [print(filename) for filename in file_path_list]

    try:
        df_list = [pd.read_csv(file, delimiter=',', header=None) for file in
                   file_path_list]
    except Exception as e:
        logging.error(f"Error reading CSV files: {e}")

        return

    # Files that will be packed than sent
    # if files_to_send > len(filename_list), then
    # it executes the list circularly
    files_to_send = 1
    logging.info("Packing data")
    packed_data_list = []
    for i in range(files_to_send):
        packed_data_list.extend(pack_file(df_list[i % (len(df_list))]))
    logging.info("Packing complete")
    time.sleep(2)

    try:
        # Create TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info("Socket open")
        sock.connect((HOST, PORT))
        logging.info("Connected")
        # send_packed_data(sock, packed_data_array)
        send_packed_data(sock, packed_data_list, SEND_RATE_HZ)

        # shutdown_command = SHUTDOWN_CMD.encode('utf-8')
        # time.sleep(10)
        # sock.sendall(shutdown_command)
    except Exception as e:
        logging.error(f"Error in socket communication: {e}")
    finally:
        logging.info("End of communication")
        sock.close()


if __name__ == '__main__':
    main()
