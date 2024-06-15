import ipywidgets as widgets
from IPython.display import display
from threading import Timer

class DynamicTableWidget:
    def __init__(self, title, rows_func, button_callback, button_text, button_style, refresh_interval):
        self.title = title
        self.refresh_interval = refresh_interval
        self.container = widgets.VBox(
            [
                widgets.Label(title, layout=widgets.Layout(width="100%", justify_content="center")),
                widgets.HTML(value="<hr style='border: 1px solid #000'>", layout=widgets.Layout(width="100%"))
            ],
            layout=widgets.Layout(overflow="hidden")
        )
        self.timer = None
        self.rows_func = rows_func
        self.button_callback = button_callback
        self.button_text = button_text
        self.button_style = button_style
    
    def new_lines(self, n):
        for _ in range(n):           
            t = widgets.VBox(
                [
                    widgets.HBox([
                        widgets.Button(description="Kill", button_style=self.button_style, layout=widgets.Layout(width="auto")),
                        widgets.Label("", layout=widgets.Layout(width="80%", justify_content="center")),
                    ]),
                    widgets.HTML(value="<hr style='border: 1px solid #000'>", layout=widgets.Layout(width="100%")),
                ],
                layout=widgets.Layout(overflow="hidden")
            )
            self.container.children = self.container.children + (t,)

    def del_lines(self, n):
        self.container.children = self.container.children[:-n]

    def get_row(self, i):
        row = self.container.children[i + 2].children
        button, label, separator = row[0].children[0], row[0].children[1], row[1]
        return button, label, separator
    
    def n_rows(self):
        return len(self.container.children) - 2

    def update(self):
        lines = self.rows_func()
        delta = len(lines) - self.n_rows()
        if delta > 0:
            self.new_lines(delta)
        elif delta < 0:
            self.del_lines(-delta)
        for i, line in enumerate(lines):
            button, label, separator = self.get_row(i)
            label.value = line.replace(" ", "\xa0") # Replace spaces with non-breaking spaces
            button._click_handlers.callbacks = []
            button.line = line
            button.on_click(lambda e: self.button_callback(e, e.line))
            if i == len(lines) - 1:
                separator.layout.display = "none"
            else:
                separator.layout.display = "block"

    def auto_update(self):
        self.update()
        
        # Schedule the next refresh
        self.timer = Timer(self.refresh_interval, self.auto_update)
        self.timer.start()

    def view(self):
        display(self.container)
        self.auto_update()

class SlurmQueueWidget(DynamicTableWidget):
    def __init__(self, ssh_client=None):
        super().__init__("Slurm Queue", self.get_slurm_queue, self.on_click, "Kill", "danger", 1)
        self.ssh_client = ssh_client

    def get_slurm_queue(self):
        _, stdout, _ = self.ssh_client.exec_command("slurm queue")
        lines = stdout.readlines()[1:]
        return lines
    
    def kill_job(self, row):
        job_id = row.split()[0]
        _, stdout, _ = self.ssh_client.exec_command(f"scancel {job_id}")

    def on_click(self, button, row):
        self.kill_job(row)