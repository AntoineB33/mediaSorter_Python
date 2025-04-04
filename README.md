File Hierarchy:

|-- .vscode
    |-- launch.json
|-- config
    |-- settings.py
|-- data
    |-- backups
        |-- v1
    |-- spreadsheets
        |-- collection_1.json
|-- resources
    |-- assets
    |-- templates
    |-- theme
|-- src
    |-- models
        |-- __init__.py
        |-- spreadsheet_model.py
    |-- qml
        |-- components
            |-- CellDelegate.qml
        |-- view
        |-- main.qml
    |-- services
    |-- __init__.py
    |-- main.py
|-- tests
    |-- gui
        |-- test_user_workflows.py
        |-- test_window_flows.py
    |-- qml
        |-- components
            |-- Test_CellDelegate.qml
        |-- models
        |-- services
        |-- Test_SpreadsheetView.qml
    |-- unit
        |-- models
            |-- __init__.py
            |-- test_spreadsheet_model.py
        |-- services
            |-- __init__.py
            |-- test_data_processing.py
    |-- __init__.py
|-- .gitignore
|-- README.md
|-- requirements.txt
|-- resources.qrc














launch.json :


{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
    
        {
            "name": "Python Debugger: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python Debugger: main.py",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "console": "integratedTerminal"
        }
    ]
}