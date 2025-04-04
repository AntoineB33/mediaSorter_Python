
|-- config
    |-- settings.py
|-- data
    |-- backups
    |-- spreadsheets
        |-- spreadsheet.json
|-- resources
    |-- templates
|-- src
    |-- models
        |-- __init__.py
        |-- spreadsheet_model.py
    |-- qml
        |-- components
            |-- CellDelegate.qml
        |-- view
        |-- main.qml
        |-- resources.qrc
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
        |-- qmltest
        |-- Test_SpreadsheetView.qml
    |-- unit
        |-- test_models
        |-- test_services
    |-- __init__.py
|-- .gitignore
|-- README.md
|-- requirements.txt














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