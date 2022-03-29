import glob
import os
from tkinter import *

from graph_utility.utility import Options


class Gui:
    def __init__(self):
        self.BACKGROUND = '#C0C0C0'
        self.FOREGROUND = '#1923E8'
        self.category = ''
        self.folder = ''
        self.results = []
        self.results_dir = os.path.join(os.path.dirname(__file__), '..\\results\\')
        self.enable_graphs = 0
        self.do_fast_graphs = 0
        self.do_consistency_check = 0
        self.write_errors = 0
        self.max_test_in_column = 5

    def set_geometry(self, root, w, h):
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def choose_directory_category(self):
        root = Tk()
        root.title('Experiments')
        root.configure(bg=self.BACKGROUND)

        # self.set_geometry(root, 250, 250)

        def set_and_continue():
            self.category = category_var.get()
            self.folder = folder_var.get()
            root.destroy()

        # Set all categories
        category_var = StringVar(root)
        category_var.set("Reachability")
        Label(root, text="Categories:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=0)
        for index, category_name in enumerate(["Reachability", "CTL", "LTL"]):
            Radiobutton(root, text=category_name, value=category_name, variable=category_var, bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1, column=0)

        # Set all available directories to choose from
        folder_var = StringVar(root)
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, '..\\results\\')
        Label(root, text="Available test directories:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=1)
        for index, test_folder in enumerate(glob.glob(results_dir + "/*/", recursive=False)):
            test_folder_name = os.path.basename(os.path.normpath(test_folder))
            if index == 0:
                folder_var.set(test_folder_name)
            Radiobutton(root, text=test_folder_name, value=test_folder_name, variable=folder_var,
                        bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1, column=1)

        Button(root, text="Choose and continue", command=set_and_continue, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(
            row=4, column=0)
        root.eval('tk::PlaceWindow . center')
        root.mainloop()

    def choose_tests_and_graph_type(self):
        directory = self.folder + "/" + self.category
        root = Tk()
        root.configure(bg=self.BACKGROUND)
        root.title(f'{directory}')
        # self.set_geometry(root, 300, 400)

        all_csv_files_in_category_in_directory = [(filename.split(self.category)[1]).replace('\\', '') for filename in
                                                  [filename for filename in
                                                   glob.glob(os.path.join(self.results_dir + directory, "*.csv"))]]
        if len(all_csv_files_in_category_in_directory) == 0:
            raise Exception(f"There are no results in selected directory: {directory}")
        results = {}
        Label(root, text=f"{directory}:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=1)

        for index, test_name in enumerate(all_csv_files_in_category_in_directory):
            column = 1
            if index > self.max_test_in_column:
                index -= self.max_test_in_column
                column = 2
            var = IntVar()
            Checkbutton(root, text=test_name.replace('.csv', ''), variable=var, bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1,
                                                 column=column,
                                                 padx=20)
            results[test_name] = var

        fast_graphs = IntVar()
        fast_graphs.set(1)
        check_consistency = IntVar()
        check_consistency.set(0)
        write_errors = IntVar()
        write_errors.set(0)
        enable_graphs = IntVar()
        enable_graphs.set(1)
        Label(root, text="Settings:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=0)
        Checkbutton(root, text='Enable graphs', variable=enable_graphs,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=1, column=0)
        Radiobutton(root, text='Fast graphs', value=1, variable=fast_graphs,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=2, column=0)
        Radiobutton(root, text='All graphs', value=0, variable=fast_graphs,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=3, column=0)
        Checkbutton(root, text='Check consistency', variable=check_consistency,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=4, column=0)
        Checkbutton(root, text='Write errors', variable=write_errors,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=5, column=0)
        Button(root, text="Select", command=root.destroy, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(row=6,
                                                                                                       column=0)
        root.eval('tk::PlaceWindow . center')
        root.mainloop()

        self.results = [csv_name for csv_name in results.keys() if results[csv_name].get() == 1]
        self.enable_graphs = enable_graphs.get()
        self.do_fast_graphs = fast_graphs.get()
        self.do_consistency_check = check_consistency.get()
        self.write_errors = write_errors.get()
        if (enable_graphs.get() == 1) and (len(self.results) == 0):
            raise Exception('You did not choose any tests')

    def get_options(self):
        self.choose_directory_category()
        self.choose_tests_and_graph_type()

        options = Options(
            result_dir=self.results_dir + self.folder + "\\" + self.category,
            graph_dir=os.path.join(os.path.dirname(__file__), f"..\\graphs\\{self.folder}\\{self.category}"),
            results_to_plot=self.results,
            category=self.category,
            folder=self.folder,
            test_names=[os.path.split(os.path.splitext(csv)[0])[1] for csv in self.results],
            chosen_graphs=[],
            chosen_lines=[],
            read_results=[],
            do_fast_graphs=bool(self.do_fast_graphs),
            do_consistency_check=bool(self.do_consistency_check),
            enable_graphs=bool(self.enable_graphs),
            write_errors=bool(self.write_errors)
        )

        if not options.enable_graphs and not options.do_consistency_check:
            raise Exception('You chose to not do graphs or consistency, you probably clicked something wrong')

        if len(options.results_to_plot) == 0:
            raise Exception('You must choose some results')

        if len(options.results_to_plot) == 1 and options.do_consistency_check:
            raise Exception('You must choose at least two results to do consistency checks')

        print("----------Options----------")
        print(f"Selected folder: {options.folder}")
        print(f"Selected category: {options.category}")
        print(f"Selected tests: {options.test_names}")
        print(f"Doing consistency check: {options.do_consistency_check}")
        print(f"Creating graphs: {options.enable_graphs}")
        if self.enable_graphs:
            if self.do_fast_graphs:
                print(f"\tDoing quick graphs")
                options.chosen_graphs = ['answers', 'rules', 'memory-state lines', 'time lines', 'size lines']
            else:
                options.chosen_graphs = ['answers', 'rules', 'memory-state lines', 'time lines', 'size lines']
                print(f"\tDoing all graphs")

        return options
