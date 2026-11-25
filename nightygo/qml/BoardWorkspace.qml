import QtQuick

Rectangle {
    id: root
    color: uiTheme === "Warm light" ? "#f3f0e9" : "#111722"
    property var controller: gameController
    property int boardSize: controller ? controller.boardSize : 19
    property var rows: controller ? controller.boardRows : []
    property int hoverX: -1
    property int hoverY: -1

    Canvas {
        id: board
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.94
        height: width
        renderTarget: Canvas.Image
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            const side = width
            const margin = side * 0.075
            const span = side - margin * 2
            const step = span / (root.boardSize - 1)
            const wood = ctx.createLinearGradient(0, 0, side, side)
            wood.addColorStop(0, "#e5bd7e")
            wood.addColorStop(0.5, "#d8aa64")
            wood.addColorStop(1, "#c89550")
            ctx.fillStyle = wood
            ctx.fillRect(0, 0, side, side)
            ctx.strokeStyle = "#47351f"
            ctx.lineWidth = Math.max(1, step * 0.025)
            for (let i = 0; i < root.boardSize; ++i) {
                const p = margin + i * step
                ctx.beginPath(); ctx.moveTo(margin, p); ctx.lineTo(side - margin, p); ctx.stroke()
                ctx.beginPath(); ctx.moveTo(p, margin); ctx.lineTo(p, side - margin); ctx.stroke()
            }
            const stars = root.boardSize === 19 ? [3, 9, 15] : root.boardSize === 13 ? [3, 6, 9] : [2, 4, 6]
            ctx.fillStyle = "#47351f"
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
                else ctx.fillStyle = color === 1 ? "#17191d" : "#faf9f4"
                ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill()
                ctx.globalAlpha = 1
                const shine = ctx.createRadialGradient(cx - radius * 0.32, cy - radius * 0.38, radius * 0.04, cx, cy, radius)
                if (color === 1 || (!color && root.controller.toPlay === 1)) {
                    shine.addColorStop(0, "rgba(255,255,255,0.46)"); shine.addColorStop(0.35, "rgba(160,175,192,0.11)"); shine.addColorStop(1, "rgba(0,0,0,0.12)")
                } else {
                    shine.addColorStop(0, "rgba(255,255,255,0.05)"); shine.addColorStop(0.62, "rgba(255,255,255,0)"); shine.addColorStop(1, "rgba(0,0,0,0.2)")
                }
                ctx.fillStyle = shine
                ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI * 2); ctx.fill()
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
        text: "NIGHTYGO  /  PLAY"
        color: uiTheme === "Warm light" ? "#292d34" : "#d7e3f4"
        font.pixelSize: 13
        font.letterSpacing: 2.2
        font.weight: Font.DemiBold
    }
    Text {
        anchors { right: parent.right; top: parent.top; margins: 18 }
        text: controller ? controller.moveCount + " moves" : ""
        color: uiTheme === "Warm light" ? "#68717d" : "#91a1b7"
        font.pixelSize: 13
    }
}
