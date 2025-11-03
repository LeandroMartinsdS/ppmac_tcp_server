# Power PMAC TCP Server

## Description

This repository provides a simple TCP server implementation for Power PMAC systems. It allows external clients to send data over TCP, which is then written to Power PMAC shared memory for control or monitoring purposes.

## Features

- Simple and efficient TCP server for Power PMAC
- Supports structured data frames (int/double)
- Easily integrates into Power PMAC IDE projects
- Can be used as a background program or library

## How to Use

Follow the steps below to add this module to your Power PMAC project:

1. Clone or add this repository as a submodule in the desired path under **C Language**.
2. In the Power PMAC IDE, right-click on the desired folder (e.g., *Background Programs* or *Libraries*) and select **"Add a new..."**.
3. Enter the name `ppmac_tcp_server` — the same name as this repository.
4. When prompted to overwrite the file, select **"No"**.
5. Right-click on the created folder and select **"Add" > "Existing item..."**.
6. Select the source (`.c`) and header (`.h`) files from this repository.

## License

This project is licensed under the **Apache 2.0 License**. See the LICENSE file for details.

## Author

[Leandro Martins dos Santos](https://github.com/LeandroMartinsdS) <br>
Software Systems Engineer <br>
Diamond Light Source Ltd. <br>
