import random
import time
from collections import deque
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Grid, ScrollableContainer, Horizontal
from textual.widgets import Header, Label, Static, Switch
from textual.message import Message
import plotext as plt
import re
import random
import time
from collections import deque
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Grid, ScrollableContainer, Horizontal
from textual.widgets import Header, Label, Static, Switch
from textual.message import Message
from textual.reactive import reactive
import plotext as plt
import re

def blueout(text: str) -> str:
    """Replace ANSI blue color sequence with Rich blue markup."""
    pattern = r'\x1b\[38;5;12m(.*?)\x1b\[0m'
    return re.sub(pattern, r'[blue]\1[/]', text)

class DataPlot(Static):
    """A plot widget that adapts to container size."""
    DEFAULT_CSS = """
    DataPlot {
        height: 100%;
        border: solid green;
        background: $surface;
        padding: 1;
        layout: vertical;
    }
    
    .plot-title {
        text-align: center;
        height: 3;
    }
    
    .plot-content {
        text-align: left;
        height: 1fr;
    }
    """

    def __init__(self, title: str, history_size: int = 30):
        super().__init__()
        self.title_text = title
        self.history = []#: deque[float] = deque(maxlen=history_size)
        self.current_value = 0.0
        self.integrated_value = 0.0
        self.plot_width = 0
        self.plot_height = 0
        self.clearturn = False

    def compose(self) -> ComposeResult:
        yield Label(self.title_text, classes="plot-title")
        yield Label(self.get_display_text(), classes="plot-content")

    def on_resize(self, event: Message) -> None:
        """Handle resize events to update plot dimensions."""
        # Get container size in characters
        self.plot_width = event.size.width - 5  # Subtract padding
        self.plot_height = event.size.height -7  # Subtract title and padding
        # Trigger a refresh of the display
        self.refresh()

    def get_ascii_plot(self) -> str:
        if not self.history:
            return "No data yet..."

        values = list(self.history)
        
        plt.clear_figure()
        # plt.clear_terminal()
        plt.plot_size(height=self.plot_height, width=self.plot_width,)
        plt.theme("pro")
        plt.title(f"{self.plot_height},{self.plot_width}")
        plt.plot(values, marker="braille")
        plt.xfrequency(4)
        plt.yfrequency(4)
        return blueout(plt.build()).replace("\x1b[0m","")

    def get_display_text(self) -> str:
        """Format the display text with current value, integrated value and plot."""
        return (f"{self.get_ascii_plot()}")

    def update_values(self, current: float, integrated: float) -> None:
        """Update both current and integrated values and the history."""
        self.current_value = current
        self.integrated_value = integrated
        self.history.append(current)
        self.query_one(".plot-content").update(self.get_display_text())

class Sidebar(ScrollableContainer):
    """A sidebar containing plot toggles."""
    DEFAULT_CSS = """
    Sidebar {
        width: 20;
        height: 100%;
        background: $panel;
        border-right: solid $primary;
        padding: 1;
        overflow-y: auto;
    }
    
    Sidebar Switch {
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the switches for each plot."""
        for i in range(6):
            yield Switch(id=f"toggle_{i}", value=True)

class AdaptiveGrid(Grid):
    """A grid that adapts its layout based on visible children."""
    
    def __init__(self):
        super().__init__()
        self.visible_count = reactive(6)
    
    def update_grid_size(self):
        """Update grid size based on number of visible plots."""
        visible = self.visible_count
        if visible <= 1:
            self.styles.grid_size = "1 1"
        elif visible == 2:
            self.styles.grid_size = "2 1"
        elif visible <= 4:
            self.styles.grid_size = "2 2"
        else:
            self.styles.grid_size = "3 2"
        
        # Adjust individual plot sizes
        for plot in self.query(DataPlot):
            if plot.styles.display == "block":
                if visible <= 1:
                    plot.styles.width = "100%"
                    plot.styles.height = "100%"
                elif visible == 2:
                    plot.styles.width = "50%"
                    plot.styles.height = "100%"
                elif visible <= 4:
                    plot.styles.width = "50%"
                    plot.styles.height = "50%"
                else:
                    plot.styles.width = "33%"
                    plot.styles.height = "50%"

class DataGeneratorApp(App):
    """Main application class."""
    CSS = """
    Horizontal {
        height: 100%;
    }
    
    Grid {
        width: 1fr;
        height: 100%;
        grid-gutter: 1;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.plots = []
        self.output_file = Path("data_log.txt")
        self.current_values = [0.0] * 6
        self.integrated_values = [0.0] * 6
        self.grid = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal():
            yield Sidebar()
            self.grid = AdaptiveGrid()
            with self.grid:
                for i in range(6):
                    plot = DataPlot(f"Signal {i+1}")
                    self.plots.append(plot)
                    yield plot

    async def on_mount(self) -> None:
        """Set up background tasks when the app starts."""
        self.output_file.write_text("")
        self.set_interval(1.0, self.update_data)

    def update_data(self) -> None:
        """Generate new random values and update the display."""
        timestamp = time.time()
        
        # Generate and integrate new values for each plot
        for i in range(6):
            self.current_values[i] = random.uniform(-1.0, 1.0)
            self.integrated_values[i] += self.current_values[i]
            self.plots[i].update_values(
                self.current_values[i],
                self.integrated_values[i]
            )

        # Write to file
        with self.output_file.open('a') as f:
            values_str = ','.join([f"{v:.3f}" for v in self.current_values])
            integrated_str = ','.join([f"{v:.3f}" for v in self.integrated_values])
            f.write(f"{timestamp},{values_str},{integrated_str}\n")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch toggle events."""
        plot_index = int(event.switch.id.split('_')[1])
        if event.value:
            self.plots[plot_index].styles.display = "block"
        else:
            self.plots[plot_index].styles.display = "none"
        
        # Count visible plots and update grid
        visible_count = sum(1 for plot in self.plots if plot.styles.display == "block")
        self.grid.visible_count = visible_count
        self.grid.update_grid_size()

if __name__ == "__main__":
    app = DataGeneratorApp()
    app.run()
