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
        self.inhib = ""
        self.search_strategy = ""
        self.all_options = False
        self.chosen_directory = ""

    def set_geometry(self, root, w, h):
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def choose_directory_category_search_type(self):
        root = Tk()
        root.title('Experiments')
        root.configure(bg=self.BACKGROUND)

        def set_and_continue():
            self.folder = folder_var.get()
            self.category = category_var.get()
            self.inhib = inhib_var.get()
            self.search_strategy = search_var.get()
            self.chosen_directory = self.folder + "/" + self.category + "/" + self.search_strategy + "/" + self.inhib
            root.destroy()

        def absolutely_everything():
            self.all_options = True
            root.destroy()

        # Set all available directories to choose from
        folder_var = StringVar(root)
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, '..\\results\\')
        Label(root, text="Available test directories:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=0)
        for index, test_folder in enumerate(glob.glob(results_dir + "/*/", recursive=False)):
            test_folder_name = os.path.basename(os.path.normpath(test_folder))
            if index == 0:
                folder_var.set(test_folder_name)
            Radiobutton(root, text=test_folder_name, value=test_folder_name, variable=folder_var,
                        bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1, column=0)

        # Set all categories column
        category_var = StringVar(root)
        category_var.set("ReachabilityCardinality")
        Label(root, text="Categories:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=1)
        categories = ["ReachabilityCardinality", "ReachabilityFireability", "CTLCardinality", "CTLFireability",
                      "LTLCardinality", "LTLFireability"]
        for index, category_name in enumerate(categories):
            Radiobutton(root, text=category_name, value=category_name, variable=category_var, bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1, column=1)

        # Set Search strategy
        search_var = StringVar(root)
        search_var.set("HEUR")
        Label(root, text="Search strategy:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=2)
        for index, search_strategy_name in enumerate(["HEUR", "DFS", "RDFS"]):
            Radiobutton(root, text=search_strategy_name, value=search_strategy_name, variable=search_var,
                        bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1, column=2)

        # Set inhib or normal
        inhib_var = StringVar(root)
        inhib_var.set("Normal")
        Label(root, text="Type:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=3)
        for index, category_name in enumerate(["Normal", "Inhib"]):
            Radiobutton(root, text=category_name, value=category_name, variable=inhib_var, bg=self.BACKGROUND,
                        fg=self.FOREGROUND).grid(row=index + 1, column=3)

        Button(root, text="Absolutely everything", command=absolutely_everything, bg=self.BACKGROUND,
               fg=self.FOREGROUND).grid(
            row=len(categories) + 1, column=0)

        Button(root, text="Choose and continue", command=set_and_continue, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(
            row=len(categories) + 1, column=3)

        root.eval('tk::PlaceWindow . center')
        root.protocol("WM_DELETE_WINDOW", sys.exit)
        root.mainloop()

    def choose_tests_and_graph_type(self):
        root = Tk()
        root.configure(bg=self.BACKGROUND)
        root.title(f'{self.chosen_directory}')

        all_csv_files_in_category_in_chosen_directory = [(filename.split(self.chosen_directory)[1]).replace('\\', '') for filename in
                                                  [filename for filename in
                                                   glob.glob(
                                                       os.path.join(self.results_dir + self.chosen_directory, "*.csv"))]]

        if len(all_csv_files_in_category_in_chosen_directory) == 0:
            raise Exception(f"There are no results in selected directory: {self.chosen_directory}")
        results = {}
        Label(root, text=f"{self.chosen_directory}:", bg=self.BACKGROUND,
              fg=self.FOREGROUND).grid(row=0, column=1)

        for index, test_name in enumerate(all_csv_files_in_category_in_chosen_directory):
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
        Checkbutton(root, text='Check consistency', variable=check_consistency,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=4, column=0)
        Checkbutton(root, text='Debug', variable=debug,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=5, column=0)
        Checkbutton(root, text='Unique results', variable=unique_results,
                    bg=self.BACKGROUND,
                    fg=self.FOREGROUND).grid(row=6, column=0)

        Button(root, text="Make graphs", command=root.destroy, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(row=7,
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
            row=8,
            column=0)
        Button(root, text="Deselect all tests", command=deselect_all_tests, bg=self.BACKGROUND,
               fg=self.FOREGROUND).grid(
            row=9,
            column=0)
        Button(root, text="EVERYTHING", command=EVERYTHING, bg=self.BACKGROUND, fg=self.FOREGROUND).grid(
            row=10,
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

        print(self.folder)
        if "CPN" in self.folder:
            self.petri_net_type = "CPN"
        elif "PT" in self.folder:
            self.petri_net_type = "PT"
        else:
            raise Exception('Could not figure out if we have results from a CPN or PT. Check directory name')

    def create_all_options(self):
        # Todo
        return []

    def get_options(self):
        self.choose_directory_category_search_type()
        if not self.all_options:
            self.choose_tests_and_graph_type()

            options = Options(
                result_dir=self.results_dir + self.chosen_directory,
                graph_dir=os.path.join(os.path.dirname(__file__), f"..\\graphs\\{self.chosen_directory}"),
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
                petri_net_type=self.petri_net_type,
                all_options=False,
                search_strategy=self.search_strategy
            )

            if self.enable_graphs == 0:
                options.chosen_graphs = []

            if self.debug:
                options.chosen_graphs.append('debug')

            if not ((
                            options.enable_graphs > 0) or options.do_consistency_check or options.debug or options.unique_results):
                raise Exception(
                    'You chose to not do graphs, consistency or debug mode, you probably clicked something wrong')

            if len(options.results_to_plot) == 0:
                raise Exception('You must choose some results')

            if len(options.results_to_plot) == 1 and (options.do_consistency_check or options.unique_results):
                raise Exception('You must choose at least two results to do consistency/unique results')

            print("---------------Options---------------")
            print("-------Chosen tests-------")
            print(f"Folder: {options.folder}")
            print(f"Category: {options.category}")
            print(f"Tests: {options.test_names}")
            print(f"Search strategy: {options.search_strategy}")
            print(f"Type of net: {options.petri_net_type}")

            print("-------Running-------")
            print(f"Doing consistency check: {options.do_consistency_check}")
            print(f"Comparing experiments to find unique results: {options.unique_results}")
            print(f"Doing debug graph and errors: {options.debug}")
            print(f"Creating graphs: {options.enable_graphs > 0}")
            if self.enable_graphs == 1:
                print(f"\tDoing quick graphs")
            elif self.enable_graphs == 2:
                print(f"\tDoing all graphs")

            return [options]
        else:
            print("Doing absolutely everything")
            return create_all_options()
