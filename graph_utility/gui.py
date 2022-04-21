import glob
import os
import sys
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
        self.do_consistency_check = 0
        self.debug = 0
        self.max_test_in_column = 11
        self.unique_results = 0
        self.petri_net_type = ""

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
        root.protocol("WM_DELETE_WINDOW", sys.exit)
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
                index -= (self.max_test_in_column + 1)
                column += 1

            var = IntVar()
            Checkbutton(root, text=test_name.replace('.csv', ''), variable=var, bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1,
                                                 column=column,
                                                 padx=20)
            results[test_name] = var

        check_consistency = IntVar()
        check_consistency.set(0)
        debug = IntVar()
        debug.set(0)
        enable_graphs = IntVar()
        enable_graphs.set(1)
        unique_results = IntVar()
        petri_net_type = StringVar()
        petri_net_type.set('CPN')
        Label(root, text="Settings:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=0)
        Radiobutton(root, text='No graphs', value=0, variable=enable_graphs,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=1, column=0)
        Radiobutton(root, text='Fast graphs', value=1, variable=enable_graphs,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=2, column=0)
        Radiobutton(root, text='All graphs', value=2, variable=enable_graphs,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=3, column=0)
        Radiobutton(root, text='PT', value='PT', variable=petri_net_type,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=4, column=0)
        Radiobutton(root, text='CPN', value='CPN', variable=petri_net_type,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=5, column=0)
        Checkbutton(root, text='Check consistency', variable=check_consistency,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=6, column=0)
        Checkbutton(root, text='Debug', variable=debug,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=7, column=0)
        Checkbutton(root, text='Unique results', variable=unique_results,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=8, column=0)

        Button(root, text="Make graphs", command=root.destroy, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(row=9,
                                                                                                            column=0)

        def select_all_tests():
            for results_var in results.values():
                results_var.set(1)

        def deselect_all_tests():
            for results_var in results.values():
                results_var.set(0)

        def EVERYTHING():
            select_all_tests()
            check_consistency.set(1)
            debug.set(1)
            enable_graphs.set(2)
            unique_results.set(1)
            root.destroy()

        Button(root, text="Select all tests", command=select_all_tests, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(
            row=10,
            column=0)
        Button(root, text="Deselect all tests", command=deselect_all_tests, bg=self.BACKGROUND,
               fg=self.FOREGROUND).grid(
            row=11,
            column=0)
        Button(root, text="EVERYTHING", command=EVERYTHING, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(
            row=12,
            column=0)
        root.eval('tk::PlaceWindow . center')

        root.protocol("WM_DELETE_WINDOW", sys.exit)
        root.mainloop()

        self.results = [csv_name for csv_name in results.keys() if results[csv_name].get() == 1]
        self.enable_graphs = enable_graphs.get()
        self.do_consistency_check = check_consistency.get()
        self.debug = debug.get()
        self.unique_results = unique_results.get()
        if (enable_graphs.get() > 0) and (len(self.results) == 0):
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
            chosen_graphs=['answers', 'rules', 'memory-state lines', 'time lines', 'size lines'],
            read_results=[],
            do_consistency_check=bool(self.do_consistency_check),
            enable_graphs=self.enable_graphs,
            debug=bool(self.debug),
            unique_results=bool(self.unique_results),
            petri_net_type=self.petri_net_type
        )

        if self.enable_graphs == 0:
            options.chosen_graphs = []

        if self.debug:
            options.chosen_graphs.append('debug')

        if not ((options.enable_graphs > 0) or options.do_consistency_check or options.debug or options.unique_results):
            raise Exception(
                'You chose to not do graphs, consistency or debug mode, you probably clicked something wrong')

        if len(options.results_to_plot) == 0:
            raise Exception('You must choose some results')

        if len(options.results_to_plot) == 1 and (options.do_consistency_check or options.unique_results):
            raise Exception('You must choose at least two results to do consistency/unique results')

        print("----------Options----------")
        print(f"Selected folder: {options.folder}")
        print(f"Selected category: {options.category}")
        print(f"Selected tests: {options.test_names}")
        print(f"Doing consistency check: {options.do_consistency_check}")
        print(f"Comparing experiments to find unique results: {options.unique_results}")
        print(f"Doing debug graph and errors: {options.debug}")
        print(f"Creating graphs: {options.enable_graphs > 0}")
        if self.enable_graphs == 1:
            print(f"\tDoing quick graphs")
        elif self.enable_graphs == 2:
            print(f"\tDoing all graphs")

        return options
