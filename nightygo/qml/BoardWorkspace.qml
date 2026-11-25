import QtQuick

Rectangle {
    id: root
    color: uiTheme === "Warm light" ? "#e9eef3" : "#0b1018"
    gradient: Gradient {
        GradientStop { position: 0.0; color: uiTheme === "Warm light" ? "#f4f7fa" : "#111c2a" }
        GradientStop { position: 1.0; color: uiTheme === "Warm light" ? "#e6ebf1" : "#090e15" }
    }
    property var controller: gameController
    property int boardSize: controller ? controller.boardSize : 19
    property var rows: controller ? controller.boardRows : []
    property int hoverX: -1
    property int hoverY: -1
    property string boardTexture: boardMaterialName
    property string stoneTexture: stoneMaterialName
    property string motion: motionLevel
    property real skyPhase: 0

    Timer {
        interval: root.motion === "full" ? 33 : 100
        repeat: true
        running: root.motion !== "off" && root.boardTexture !== "Classic wood"
        onTriggered: {
            root.skyPhase += root.motion === "subtle" ? 0.018 : 0.055
            board.requestPaint()
        }
    }

    Rectangle {
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.94 + 16
        height: width
        z: 1
        radius: 18
        color: uiTheme === "Warm light" ? "#d3dce5" : "#202c3b"
        border.color: uiTheme === "Warm light" ? "#bdc8d3" : "#34475e"
        border.width: 1
    }
    Rectangle {
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 7
        width: Math.min(parent.width, parent.height) * 0.94 + 8
        height: width
        radius: 17
        color: "#000000"
        opacity: uiTheme === "Warm light" ? 0.06 : 0.22
        z: 0
    }
    Canvas {
        id: board
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.94
        height: width
        z: 2
        renderTarget: Canvas.Image
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            const side = width
            const margin = side * 0.075
            const span = side - margin * 2
            const step = span / (root.boardSize - 1)
            const wood = ctx.createLinearGradient(0, 0, side, side)
            if (root.boardTexture === "Starfield") {
                wood.addColorStop(0, "#17153b")
                wood.addColorStop(0.5, "#101c3b")
                wood.addColorStop(1, "#080d21")
            } else if (root.boardTexture === "Night sky") {
                wood.addColorStop(0, "#263a61")
                wood.addColorStop(0.5, "#172847")
                wood.addColorStop(1, "#101a34")
            } else {
                wood.addColorStop(0, "#e5bd7e")
                wood.addColorStop(0.5, "#d8aa64")
                wood.addColorStop(1, "#c89550")
            }
            ctx.fillStyle = wood
            ctx.fillRect(0, 0, side, side)
            if (root.boardTexture !== "Classic wood") {
                const glow = ctx.createRadialGradient(
                    side * (0.5 + 0.22 * Math.cos(root.skyPhase)),
                    side * (0.5 + 0.2 * Math.sin(root.skyPhase)),
                    0, side * 0.5, side * 0.5, side * 0.58
                )
                glow.addColorStop(0, root.boardTexture === "Starfield" ? "rgba(102,75,220,0.34)" : "rgba(83,177,218,0.28)")
                glow.addColorStop(1, "rgba(10,15,35,0)")
                ctx.fillStyle = glow
                ctx.fillRect(0, 0, side, side)
                for (let i = 0; i < 180; ++i) {
                    const x = ((i * 0.61803398875 + root.skyPhase * 0.006) % 1) * side
                    const y = ((i * 0.75487766625 + 0.17) % 1) * side
                    const alpha = 0.22 + 0.48 * (0.5 + 0.5 * Math.sin(root.skyPhase * 2 + i * 1.7))
                    ctx.fillStyle = `rgba(232,240,255,${alpha})`
                    ctx.beginPath(); ctx.arc(x, y, i % 13 === 0 ? 1.5 : 0.8, 0, Math.PI * 2); ctx.fill()
                }
            }
            ctx.strokeStyle = root.boardTexture === "Classic wood" ? "#47351f" : "rgba(210,225,255,0.72)"
            ctx.lineWidth = Math.max(1, step * 0.025)
            for (let i = 0; i < root.boardSize; ++i) {
                const p = margin + i * step
                ctx.beginPath(); ctx.moveTo(margin, p); ctx.lineTo(side - margin, p); ctx.stroke()
                ctx.beginPath(); ctx.moveTo(p, margin); ctx.lineTo(p, side - margin); ctx.stroke()
            }
            const stars = root.boardSize === 19 ? [3, 9, 15] : root.boardSize === 13 ? [3, 6, 9] : [2, 4, 6]
            ctx.fillStyle = root.boardTexture === "Classic wood" ? "#47351f" : "#e5efff"
            for (const x of stars) for (const y of stars) {
                ctx.beginPath(); ctx.arc(margin + x * step, margin + y * step, step * 0.09, 0, Math.PI * 2); ctx.fill()
            }
            for (let y = 0; y < root.boardSize; ++y) for (let x = 0; x < root.boardSize; ++x) {
                const color = root.rows.length ? root.rows[y][x] : 0
                const cx = margin + x * step, cy = margin + y * step, radius = step * 0.44
                if (!color && x === root.hoverX && y === root.hoverY) {
                    ctx.globalAlpha = 0.48
                    ctx.fillStyle = root.controller && root.controller.toPlay === 1 ? "#17191d" : "#faf9f4"
                } else if (!color) continue
                else if (root.stoneTexture === "Starfield") ctx.fillStyle = color === 1 ? "#172040" : "#dce9ff"
                else if (root.stoneTexture === "Moonstone") ctx.fillStyle = color === 1 ? "#30323b" : "#e6e5ec"
                else ctx.fillStyle = color === 1 ? "#17191d" : "#faf9f4"
                const stoneFill = ctx.createRadialGradient(cx - radius * 0.32, cy - radius * 0.38, radius * 0.04, cx, cy, radius)
                if (color === 1 || (!color && root.controller.toPlay === 1)) {
                    stoneFill.addColorStop(0, root.stoneTexture === "Starfield" ? "#7180bd" : "#4a4e5a")
                    stoneFill.addColorStop(0.42, root.stoneTexture === "Starfield" ? "#252e58" : "#24262e")
                    stoneFill.addColorStop(1, root.stoneTexture === "Starfield" ? "#090f22" : "#08090d")
                } else {
                    stoneFill.addColorStop(0, "#ffffff")
                    stoneFill.addColorStop(0.62, root.stoneTexture === "Starfield" ? "#dbe7ff" : "#e6e5ed")
                    stoneFill.addColorStop(1, root.stoneTexture === "Starfield" ? "#8795b9" : "#92939c")
                }
                ctx.fillStyle = stoneFill
                ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill()
                ctx.globalAlpha = 1
            }
        }
        Connections {
            target: root.controller
            function onStateChanged() { board.requestPaint() }
        }
        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            function pointAt(mouse) {
                const margin = board.width * 0.075
                const step = (board.width - margin * 2) / (root.boardSize - 1)
                const px = Math.round((mouse.x - margin) / step)
                const py = Math.round((mouse.y - margin) / step)
                if (px < 0 || py < 0 || px >= root.boardSize || py >= root.boardSize) return [-1, -1]
                return [px, py]
            }
            onPositionChanged: function(mouse) {
                const p = pointAt(mouse)
                if (p[0] !== root.hoverX || p[1] !== root.hoverY) {
                    root.hoverX = p[0]; root.hoverY = p[1]; board.requestPaint()
                }
            }
            onExited: { root.hoverX = -1; root.hoverY = -1; board.requestPaint() }
            onClicked: function(mouse) { const p = pointAt(mouse); if (p[0] >= 0 && root.controller) root.controller.play_at(p[0], p[1]) }
        }
    }
    Text {
        anchors { left: parent.left; top: parent.top; margins: 18 }
        text: {
            const labels = {en: "NIGHTYGO  /  PLAY", zh_TW: "NIGHTYGO  /  對局", zh_CN: "NIGHTYGO  /  对局", ja: "NIGHTYGO  /  対局", ko: "NIGHTYGO  /  대국"}
            return labels[uiLanguage] || labels.en
        }
        color: uiTheme === "Warm light" ? "#292d34" : "#d7e3f4"
        font.pixelSize: uiFontSize + 2
        font.letterSpacing: 2.2
        font.weight: Font.DemiBold
    }
    Text {
        anchors { right: parent.right; top: parent.top; margins: 18 }
        text: {
            if (!controller) return ""
            const suffix = {en: " moves", zh_TW: " 手", zh_CN: " 手", ja: "手", ko: "수"}
            return controller.moveCount + (suffix[uiLanguage] || suffix.en)
        }
        color: uiTheme === "Warm light" ? "#68717d" : "#91a1b7"
        font.pixelSize: uiFontSize + 2
    }
}
