import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "./components"

Window {
    id: mainWindow
    width: 800
    height: 600
    visible: true
    title: "Dynamic Spreadsheet"

    MainLayout {
        id: mainLayout
    }
    
    FloatingWindow {
        id: floatingWindow
        tableView: mainLayout.tableView
    }

    Connections {
        target: spreadsheetModel
        function onSignal(data) {
            switch (data.type) {
                case "input_text_changed":
                    inputField.text = data.value;
                    break;
                case "layoutTimer_restart":
                    mainLayout.tableView.layoutTimer.restart();
                    break;
                case "FloatingWindow_text_changed":
                    floatingWindow.errorTextItem.text = data.value;
                    break;
                case "selected_cell_changed":
                    selectedRow = data.row;
                    selectedColumn = data.column;
                    break;
                default:
                    console.warn("Unknown signal type:", data.type);
            }
        }
    }

}