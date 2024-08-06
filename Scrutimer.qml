import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 1024
    height: 700
    x: screen.desktopAvailableWidth - width - 12
    y: screen.desktopAvailableHeight - height - 48
    title: "Scrutimer"
    flags: Qt.FramelessWindowHint | Qt.Window
    property string currTime: "00:00:00"
    property QtObject backend
    property var hms: {'hours': 0, 'minutes': 0, 'seconds': 0 }

    Rectangle {
        anchors.fill: parent

        Image {
            sourceSize.width: parent.width
            sourceSize.height: parent.height
            source: "./images/Scrutimer_BG_1024_720.png"
            fillMode: Image.PreserveAspectCrop
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"

            Image {
                id: clockface
                sourceSize.height: parent.height
                fillMode: Image.PreserveAspectFit
                /*
                source: "./images/clockface.png"
                */
                source: "./images/Scrutimer_clockface.svg"

                Image {
                    x: clockface.width/2 - width/2
                    y: (clockface.height/2) - height/2
                    scale: clockface.width/1000
                    source: "./images/Scrutimer_Hour.svg"
                    transform: Rotation {
                        origin.x: 500; origin.y: 500;
                        angle: (hms.hours * 30) + (hms.minutes * 0.5) + (hms.seconds / 120)
                    }
                }

                Image {
                    x: clockface.width/2 - width/2
                    y: clockface.height/2 - height/2
                    source: "./images/Scrutimer_Minute.svg"
                    scale: clockface.width/1000
                    transform: Rotation {
                        origin.x: 500; origin.y: 500;
                        angle: (hms.minutes * 6) + (hms.seconds * 0.1)
                        Behavior on angle {
                            SpringAnimation { spring: 1; damping: 0.2; modulus: 360 }
                        }
                    }
                }

                Image {
                    x: clockface.width/2 - width/2
                    y: clockface.height/2 - height/2
                    source: "./images/Scrutimer_Second.svg"
                    scale: clockface.width/1000
                    transform: Rotation {
                        origin.x: 500; origin.y: 500;
                        angle: hms.seconds * 6
                        Behavior on angle {
                            SpringAnimation { spring: 1; damping: 0.2; modulus: 360 }
                        }
                    }
                }

                /*
                Image {
                    x: clockface.width/2 - width/2
                    y: clockface.height/2 - height/2
                    source: "./images/cap.png"
                    scale: clockface.width/465
                }
                */

            }

            Text {
                anchors {
                    bottom: parent.bottom
                    bottomMargin: 12
                    right: parent.right
                    leftMargin: 12
                }
                text: currTime  // used to be; text: "16:38:33"
                font.pixelSize: 48
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
    }

}
