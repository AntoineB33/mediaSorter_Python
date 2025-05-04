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
        tableView: mainLayout.tableView
    }

}