from nicegui import ui

from typing import Callable

class ATMParamaterInput:

    def __init__(
        self, 
        updatePulseFunc: Callable[[float | None, float | None, float | None, float | None, float | None, float | None, float | None], None],
        savePulseFunc: Callable[[str | None], None]
    ) -> None:

        # Update Function
        self.updatePulseFunc = updatePulseFunc

        #Save pulse function
        self.savePulseFunc = savePulseFunc
        return

    def collectAndUpdate(self) -> None:
        self.updatePulseFunc(self.totalTimeInput.value,
                             self.riseTimeInput.value,
                             self.fallTimeInput.value,
                             self.maxAmplitudeInput.value,
                             self.maxFrequencyInput.value,
                             self.risingGradientInput.value,
                             self.fallingGradientInput.value)
        return

    def initializeParameterInput(self):

        with ui.card().classes('row-span-2'):

            self.totalTimeInput = ui.number(label="Total Time (us)", 
                                            min=4,
                                            precision=1, 
                                            step=1,
                                            value=100).props("size=16")
            self.riseTimeInput = ui.number(label="Rise Time (us)", 
                                           min=1,
                                           precision=1, 
                                           step=1,
                                           value=10).props("size=16")
            self.fallTimeInput = ui.number(label="Fall Time (us)", 
                                           min=1,
                                           precision=1, 
                                           step=1,
                                           value=75).props("size=16")

            self.maxAmplitudeInput = ui.number(label="Rabi Frequency (MHz)", 
                                               min=0,
                                               precision=3, 
                                               step=0.01,
                                               value=1.00).props("size=16")
            self.maxFrequencyInput = ui.number(label="Max Frequency (MHz)", 
                                               min=0,
                                               precision=3, 
                                               step=0.01,
                                               value=1.00).props("size=16")

            self.risingGradientInput = ui.number(label="Rising Gradient",
                                                 min=0,
                                                 max=1,
                                                 precision=3,
                                                 step=0.01,
                                                 value=0.95).props("size=16")
            self.fallingGradientInput = ui.number(label="Falling Gradient",
                                                  min=0, 
                                                  max=1,
                                                  precision=3,
                                                  step=0.01,
                                                  value=0.05).props("size=16")

            self.updatePulseButton = ui.button(text="Update Pulse",
                                               on_click=self.collectAndUpdate)

            with ui.dialog() as dialog, ui.card():
                ui.label('Save as...')
                filename = ui.input('filename', value='atm_pulse')

                def save():
                    self.savePulseFunc(filename.value)
                    # ui.download.file(filename.value)
                    dialog.close()
                ui.button('Save', on_click=save)

            self.savePulseButton = ui.button('Save Pulse', on_click=dialog.open)

        return
