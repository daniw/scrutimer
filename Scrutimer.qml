import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    /*
    width: 1024
    height: 700
    x: screen.desktopAvailableWidth - width - 12
    y: screen.desktopAvailableHeight - height - 48
    */
    width: screen.desktopAvailableWidth
    height: screen.desktopAvailableHeight
    x: 0
    y: 0
    title: "Scrutimer"
    flags: Qt.FramelessWindowHint | Qt.Window

    // GUI configuration
    property var clock_border: 50
    property var clock_width_px: 1000
    property var title_size: 80
    property var text_size: 48
    property var text_top_margin: 12
    property var dig_clock_size: 64

    // Variables for synchronisation with backend
    property QtObject backend
    property string currTime: "00:00:00"
    property var hms: {'hours': 0, 'minutes': 0, 'seconds': 0 }
    property string accumulator_text: "A"
    property string electrical_text:  "E"
    property string mechanical_text:    "M"

    Rectangle {
        anchors.fill: parent

        // Background
        Image {
            sourceSize.width: parent.width
            sourceSize.height: parent.height
            source: "./images/Scrutimer_Background.svg"
            fillMode: Image.PreserveAspectCrop
        }

        // Clock
        Rectangle {
            anchors.fill: parent
            color: "transparent"

            Image {
                // Clock face
                id: clockface
                sourceSize.height: parent.height- 2 * clock_border
                x: clock_border
                y: clock_border
                fillMode: Image.PreserveAspectFit
                source: "./images/Scrutimer_clockface.svg"

                // Clock Hours
                Image {
                    x: clockface.width/2 - width/2
                    y: (clockface.height/2) - height/2
                    scale: clockface.width/clock_width_px
                    source: "./images/Scrutimer_Hour.svg"
                    transform: Rotation {
                        origin.x: clock_width_px/2; origin.y: clock_width_px/2;
                        angle: (hms.hours * 30) + (hms.minutes * 0.5) + (hms.seconds / 120)
                    }
                }

                // Clock Minutes
                Image {
                    x: clockface.width/2 - width/2
                    y: clockface.height/2 - height/2
                    source: "./images/Scrutimer_Minute.svg"
                    scale: clockface.width/clock_width_px
                    transform: Rotation {
                        origin.x: clock_width_px/2; origin.y: clock_width_px/2;
                        angle: (hms.minutes * 6) + (hms.seconds * 0.1)
                        Behavior on angle {
                            SpringAnimation { spring: 5; damping: 1.0; modulus: 360 }
                        }
                    }
                }

                // Clock Seconds
                Image {
                    x: clockface.width/2 - width/2
                    y: clockface.height/2 - height/2
                    source: "./images/Scrutimer_Second.svg"
                    scale: clockface.width/clock_width_px
                    transform: Rotation {
                        origin.x: clock_width_px/2; origin.y: clock_width_px/2;
                        angle: hms.seconds * 6
                        Behavior on angle {
                            SpringAnimation { spring: 5; damping: 1.0; modulus: 360 }
                        }
                    }
                }

                // Clock Center Cap
                Image {
                    x: clockface.width/2 - width/2
                    y: clockface.height/2 - height/2
                    source: "./images/Scrutimer_Cap.svg"
                    scale: clockface.width/clock_width_px
                }

            }

            // A-Scruti Slot
            Text {
                anchors {
                    top: parent.top
                    topMargin: text_top_margin
                    left: parent.left
                    leftMargin: text_top_margin + clockface.width+ 2*clock_border
                }
                text: "Accumulator Inspection"
                font.pixelSize: title_size
                color: "black"
            }

            Text {
                anchors {
                    top: parent.top
                    topMargin: text_top_margin + title_size
                    left: parent.left
                    leftMargin: text_top_margin + clockface.width+ 2*clock_border
                }
                text: accumulator_text
                font.pixelSize: text_size
                color: "black"
            }

            // E-Scruti Slot
            Text {
                anchors {
                    top: parent.top
                    topMargin: text_top_margin + screen.desktopAvailableHeight / 3
                    left: parent.left
                    leftMargin: text_top_margin + clockface.width+ 2*clock_border
                }
                text: "Electrical Inspection"
                font.pixelSize: title_size
                color: "black"
            }

            Text {
                anchors {
                    top: parent.top
                    topMargin: text_top_margin + title_size + screen.desktopAvailableHeight / 3
                    left: parent.left
                    leftMargin: text_top_margin + clockface.width+ 2*clock_border
                }
                text: electrical_text
                font.pixelSize: text_size
                color: "black"
            }

            // M-Scruti Slot
            Text {
                anchors {
                    top: parent.top
                    topMargin: text_top_margin + screen.desktopAvailableHeight * 2 / 3
                    left: parent.left
                    leftMargin: text_top_margin + clockface.width+ 2*clock_border
                }
                text: "Mechanical Inspection"
                font.pixelSize: title_size
                color: "black"
            }

            Text {
                anchors {
                    top: parent.top
                    topMargin: text_top_margin + title_size + screen.desktopAvailableHeight * 2 / 3
                    left: parent.left
                    leftMargin: text_top_margin + clockface.width+ 2*clock_border
                }
                text: mechanical_text
                font.pixelSize: text_size
                color: "black"
            }

            // Dgital clock
            Text {
                anchors {
                    bottom: parent.bottom
                    bottomMargin: 12
                    left: parent.left
                    leftMargin: 12
                }
                text: currTime  // used to be; text: "16:38:33"
                font.pixelSize: dig_clock_size
                color: "black"
            }

        }

    }

    Connections {
        target: backend

        function onUpdated(msg) {
            currTime = msg;
        }

        function onHms(hours, minutes, seconds) {
            hms = {'hours': hours, 'minutes': minutes, 'seconds': seconds }
        }

        function onAccumulator_text(slot_a) {
            accumulator_text = slot_a;
        }

        function onElectrical_text(slot_e) {
            electrical_text = slot_e;
        }

        function onMechanical_text(slot_m) {
            mechanical_text = slot_m;
        }
    }

}
