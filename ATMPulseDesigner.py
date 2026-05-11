from nicegui import ui

from PulseDesigner.atm_inspector_page import ATMInspectorPage

if __name__ == "__main__" :

    inspectorPage = ATMInspectorPage()

    ui.run(
        title="ATM Pulse Inspector",
        dark=True,
        show=True,
        port=8090,
        reload = False,
    )
