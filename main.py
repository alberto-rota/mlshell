import asyncio
import random
import time
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Header, Label, Static
from textual.reactive import reactive
import plotext as plt

class DataContainer(Static):
    """A container showing current and integrated values."""
    DEFAULT_CSS = """
    DataContainer {
        height: 100%;
        border: solid green;
        background: $surface;
        padding: 1;
        layout: vertical;
    }
    
    .container-title {
        text-align: center;
        height: auto;
    }
    
    .container-value {
        text-align: center;
        height: auto;
        content-align: center middle;
    }
    """

    def __init__(self, title: str = "Container"):
        super().__init__()
        self.title_text = title
        self.current_value = 0.0
        self.integrated_value = 0.0

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label(self.title_text, classes="container-title")
        yield Label(self.get_display_text(), classes="container-value")

    def get_display_text(self) -> str:
        """Format the display text with current and integrated values."""
        
        return f"Current: {self.current_value:.3f}\nIntegrated: {self.integrated_value:.3f}"

    def update_values(self, current: float, integrated: float) -> None:
        """Update both current and integrated values."""
        self.current_value = current
        self.integrated_value = integrated
        self.query_one(".container-value").update(self.get_display_text())

class DataGeneratorApp(App):
    """Main application class."""
    CSS = """
    Grid {
        grid-size: 3 2;
        grid-gutter: 1;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.containers = []
        self.output_file = Path("data_log.txt")
        # Initialize arrays for current and integrated values
        self.current_values = [0.0] * 6
        self.integrated_values = [0.0] * 6

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Grid():
            for i in range(6):
                container = DataContainer(f"Signal {i+1}")
                self.containers.append(container)
                yield container

    async def on_mount(self) -> None:
        """Set up background tasks when the app starts."""
        # Clear the file at start
        self.output_file.write_text("")
        self.set_interval(1.0, self.update_data)

    def update_data(self) -> None:
        """Generate new random values and update the display."""
        timestamp = time.time()
        
        # Generate and integrate new values for each container
        for i in range(6):
            # Generate new random value between -1 and 1
            self.current_values[i] = random.uniform(-1.0, 1.0)
            # Integrate (simple sum)
            self.integrated_values[i] += self.current_values[i]
            # Update the container display
            self.containers[i].update_values(
                self.current_values[i],
                self.integrated_values[i]
            )

        # Write to file
        with self.output_file.open('a') as f:
            values_str = ','.join([f"{v:.3f}" for v in self.current_values])
            integrated_str = ','.join([f"{v:.3f}" for v in self.integrated_values])
            f.write(f"{timestamp},{values_str},{integrated_str}\n")

if __name__ == "__main__":
    app = DataGeneratorApp()
    app.run()