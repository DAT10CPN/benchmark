import glob
import os
import sys
import random
from tkinter import *

from graph_utility.utility import Options


class Gui:
    def __init__(self):
        self.BACKGROUNDS = ['#101022', '#C0C0C0', '#F7F', '#EECF6D', '#230C0F', '#201E1F', '#4A412A', '#ff0000',
                            '#0049B7']
        self.FOREGROUNDS = ['#90B0B0', '#1923E8', '#3BE', '#8B6220', '#CBA328', '#FF4000', '#2A324A', '#ffffff',
                            '#ff1d58']
        self.hexvalues = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
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
        self.search_strategy = ""
        self.all_options = False
        self.chosen_directory = ""
        self.categories = ["ReachabilityCardinality", "ReachabilityFireability", "CTLCardinality", "CTLFireability",
                           "LTLCardinality", "LTLFireability"]
        self.col_model_folders = ["MCC2021-COL", "MCC2021-COL-inhib"]
        self.pt_model_folders = ["MCC2021", "MCC2021-inhib"]
        self.search_strategies = ["BestFS", "DFS", "RDFS"]
        self.graph_names = ['answers', 'rules', 'memory-state lines', 'time lines', 'size lines',
                            'ratios', 'model-ratios', 'model-ratios-average', 'time-saved', 'answers by model']
        self.overwrite = True
        self.current_widgets = []
        self.root = None
        self.only_one_test_setup = False
        self.base_name = 'base'
        self.results_for_exam = ['C.csv', 'D.csv', 'E.csv', 'F.csv', 'I.csv', 'Q.csv', 'U.csv', 'IUC.csv',
                                 'IUDCEFQ.csv', 'base.csv']
        self.ss_for_exam = ["DFS"]
        self.model_folders_for_exam = ['MCC2021-COL']

        if os.path.exists('theme.txt'):
            with open("theme.txt", mode='r') as file:
                self.current_theme = int(file.readline())
        else:
            self.current_theme = 0

    def switch_color(self):
        self.current_theme = (self.current_theme + 1) % len(self.FOREGROUNDS)
        foreground = self.FOREGROUNDS[self.current_theme]
        background = self.BACKGROUNDS[self.current_theme]
        self.root.configure(bg=background)
        for wid in self.current_widgets:
            wid.configure(bg=background)
            wid.configure(fg=foreground)

    def switch_color_random(self):
        background = self.random_hex_color()
        self.root.configure(bg=background)
        foreground = self.random_hex_color()
        print(f"Background: {background}, Foreground: {foreground}")
        for wid in self.current_widgets:
            wid.configure(bg=background)
            wid.configure(fg=foreground)

    def random_hex_color(self):
        col = "#"
        while len(col) < 7:
            col += random.sample(self.hexvalues, 1)[0]
        return col

    def switch_color_wacky(self):
        self.root.configure(bg=self.random_hex_color())
        for wid in self.current_widgets:
            wid.configure(bg=self.random_hex_color())
            wid.configure(fg=self.random_hex_color())

    def set_geometry(self, root, w, h):
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def add_to_grid_and_current_widget(self, wid, row, column):
        self.current_widgets.append(wid)
        wid.grid(row=row, column=column)

    def create_check_button(self, text, variable, row, column):
        btn = Checkbutton(self.root, text=text, variable=variable, bg=self.BACKGROUNDS[self.current_theme],
                          fg=self.FOREGROUNDS[self.current_theme])
        self.add_to_grid_and_current_widget(btn, row, column)

    def create_radio_button(self, text, value, variable, row, column):
        btn = Radiobutton(self.root, text=text, value=value, variable=variable, bg=self.BACKGROUNDS[self.current_theme],
                          fg=self.FOREGROUNDS[self.current_theme])
        self.add_to_grid_and_current_widget(btn, row, column)

    def create_label(self, text, row, column):
        lbl = Label(self.root, text=text, bg=self.BACKGROUNDS[self.current_theme],
                    fg=self.FOREGROUNDS[self.current_theme])
        self.add_to_grid_and_current_widget(lbl, row, column)

    def create_button(self, text, command, row, column):
        btn = Button(self.root, text=text, command=command,
                     bg=self.BACKGROUNDS[self.current_theme],
                     fg=self.FOREGROUNDS[self.current_theme])
        self.add_to_grid_and_current_widget(btn, row, column)

    def are_there_results_in_dir(self):
        all_csv_files_in_category_in_chosen_directory = [
            (filename.split(self.chosen_directory)[1]).replace('\\', '')
            for filename in
            [filename for filename in
             glob.glob(
                 os.path.join(self.results_dir + self.chosen_directory,
                              "*.csv"))]]
        return len(all_csv_files_in_category_in_chosen_directory) > 0

    def choose_directory_category_search_type(self):
        root = Tk()
        root.title('Experiments')
        root.configure(bg=self.BACKGROUNDS[self.current_theme])
        self.root = root



        def set_and_continue():
            self.folder = folder_var.get()
            self.category = category_var.get()
            self.search_strategy = search_var.get()
            self.model_folder = model_folder_var.get()
            self.chosen_directory = self.folder + "/" + self.category + "/" + self.search_strategy + "/" + self.model_folder
            self.overwrite = bool(overwrite_var.get())
            root.destroy()

        def set_and_continue_random():
            self.folder = random.sample(glob.glob(self.results_dir + "/*/", recursive=False), 1)[0].split("results")[1]
            self.category = random.sample(self.categories, 1)[0]
            self.search_strategy = random.sample(self.search_strategies, 1)[0]
            self.model_folder = model_folder_var.get()
            self.chosen_directory = self.folder + self.category + "\\" + self.search_strategy + "\\" + self.model_folder
            self.overwrite = True
            root.destroy()

        def absolutely_everything():
            self.all_options = True
            self.overwrite = bool(overwrite_var.get())
            self.only_one_test_setup = bool(only_one_test_setup_var.get())
            self.folder = folder_var.get()
            root.destroy()

        # Set all available directories to choose from
        folder_var = StringVar(root)
        folder_var.set('CPN-4-30-4-2-ioless')
        self.create_label(text="Available test directories:", row=0, column=0)
        for index, test_folder in enumerate(glob.glob(self.results_dir + "/*/", recursive=False)):
            test_folder_name = os.path.basename(os.path.normpath(test_folder))
            self.create_radio_button(text=test_folder_name, value=test_folder_name, variable=folder_var,
                                     row=index + 1, column=0)

        model_folder_var = StringVar(root)
        model_folder_var.set("MCC2021-COL")
        self.create_label(text="Model Folder:", row=0, column=3)
        for index, category_name in enumerate(self.col_model_folders + self.pt_model_folders):
            self.create_radio_button(text=category_name, value=category_name, variable=model_folder_var,
                                     row=index + 1, column=3)

        # Set all categories column
        category_var = StringVar(root)
        category_var.set("ReachabilityCardinality")
        self.create_label(text="Categories:", row=0, column=1)
        for index, category_name in enumerate(self.categories):
            self.create_radio_button(text=category_name, value=category_name, variable=category_var,
                                     row=index + 1, column=1)

        # Set Search strategy
        search_var = StringVar(root)
        search_var.set("DFS")
        self.create_label(text="Search Strategy:", row=0, column=2)
        for index, search_strategy_name in enumerate(self.search_strategies):
            self.create_radio_button(text=search_strategy_name, value=search_strategy_name, variable=search_var,
                                     row=index + 1, column=2)

        only_one_test_setup_var = IntVar(root)
        only_one_test_setup_var.set(0)
        self.create_check_button(text="Only one test setup", variable=only_one_test_setup_var, row=len(self.categories),
                                 column=0)
        self.create_button(text="Absolutely everything (DFS)", command=absolutely_everything, row=len(self.categories) + 1,
                           column=0)

        overwrite_var = IntVar()
        overwrite_var.set(1)
        self.create_check_button(text='Overwrite graphs', variable=overwrite_var,
                                 row=len(self.categories) + 1, column=1)

        self.create_button(text="Party", command=self.switch_color_wacky, row=len(self.categories) - 1, column=2)
        self.create_button(text="Random theme", command=self.switch_color_random, row=len(self.categories), column=2)
        self.create_button(text="Change theme", command=self.switch_color, row=len(self.categories) + 1, column=2)
        self.create_button(text="I'm feeling lucky!", command=set_and_continue_random, row=len(self.categories),
                           column=3)
        self.create_button(text="Choose and continue", command=set_and_continue, row=len(self.categories) + 1, column=3)

        root.eval('tk::PlaceWindow . center')
        root.protocol("WM_DELETE_WINDOW", sys.exit)
        root.mainloop()

        if not self.are_there_results_in_dir() and not self.all_options:
            print(f"\033[93mThere are no results in selected directory: \033[0m{self.chosen_directory}")
            return False
        return True

    def choose_tests_and_graph_type(self):
        self.current_widgets = []
        root = Tk()
        self.root = root
        root.configure(bg=self.BACKGROUNDS[self.current_theme])
        root.title(f'{self.chosen_directory}')

        all_csv_files_in_category_in_chosen_directory = [(filename.split(self.chosen_directory)[1]).replace('\\', '')
                                                         for filename in
                                                         [filename for filename in
                                                          glob.glob(
                                                              os.path.join(self.results_dir + self.chosen_directory,
                                                                           "*.csv"))]]

        results = {}
        self.create_label(text=f"{self.chosen_directory}:", row=0, column=1)

        for index, test_name in enumerate(all_csv_files_in_category_in_chosen_directory):
            column = 1
            if index > self.max_test_in_column:
                index -= (self.max_test_in_column + 1)
                column += 1

            var = IntVar()
            self.create_check_button(text=test_name.replace('.csv', ''), variable=var,
                                     row=index + 1, column=column)
            results[test_name] = var

        check_consistency = IntVar()
        check_consistency.set(0)
        debug = IntVar()
        debug.set(0)
        enable_graphs = IntVar()
        enable_graphs.set(1)
        unique_results = IntVar()
        self.create_label(text="Settings:", row=0, column=0)

        self.create_radio_button(text='No graphs', value=0, variable=enable_graphs,
                                 row=1, column=0)

        self.create_radio_button(text='Fast graphs', value=1, variable=enable_graphs,
                                 row=2, column=0)

        self.create_radio_button(text='All graphs', value=2, variable=enable_graphs,
                                 row=3, column=0)

        self.create_check_button(text='Check consistency', variable=check_consistency,
                                 row=4, column=0)

        self.create_check_button(text='Debug', variable=debug,
                                 row=5, column=0)

        self.create_check_button(text='Unique results', variable=unique_results,
                                 row=6, column=0)

        self.create_button(text="Make Graphs", command=root.destroy, row=7,
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

        self.create_button(text="Select all tests", command=select_all_tests, row=8, column=0)
        self.create_button(text="Deselect all tests", command=deselect_all_tests, row=9, column=0)
        self.create_button(text="EVERYTHING", command=EVERYTHING, row=10, column=0)

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

        if "CPN" in self.folder:
            self.petri_net_type = "CPN"
        elif "PT" in self.folder:
            self.petri_net_type = "PT"
        else:
            raise Exception('Could not figure out if we have results from a CPN or PT. Check directory name')

    def create_single_option(self, folder_path, category, search_strategy, model_folder):
        if "CPN" in folder_path:
            petri_net_type = "CPN"
        elif "PT" in folder_path:
            petri_net_type = "PT"
        else:
            raise Exception('Could not figure out if we have results from a CPN or PT. Check directory name')

        chosen_directory = folder_path + category + "\\" + search_strategy + "\\" + model_folder

        # results = [(filename.split(chosen_directory)[1]).replace('\\', '') for filename in
        #           [filename for filename in
        #            glob.glob(
        #                os.path.join(chosen_directory, "*.csv"))]]
        results = self.results_for_exam

        folder_name = folder_path.split('results')[1].replace('\\', '')

        options = Options(
            result_dir=chosen_directory,
            graph_dir=os.path.join(os.path.dirname(__file__),
                                   f"..\\graphs\\{folder_name}\\{category}\\{search_strategy}\\{model_folder}"),
            results_to_plot=results,
            category=category,
            folder=folder_path,
            test_names=[os.path.split(os.path.splitext(csv)[0])[1] for csv in results],
            chosen_graphs=self.graph_names,
            read_results=[],
            do_consistency_check=True,
            enable_graphs=2,
            debug=False,
            unique_results=True,
            petri_net_type=petri_net_type,
            all_options=True,
            search_strategy=search_strategy,
            base_name=self.base_name,
            overwrite=self.overwrite,
            folder_name=folder_name,
            model_folder=model_folder,
            chosen_directory=f"{folder_name}\\{category}\\{search_strategy}\\{model_folder}"
        )

        return options

    def create_all_options(self):
        all_options = []
        folders = [path for path in glob.glob(f'{self.results_dir}/*/')]
        for folder_path in folders:
            if self.only_one_test_setup and not self.folder in folder_path:
                continue
            for category in self.categories:
                for search_strategy in self.ss_for_exam:
                    if "CPN" in folder_path:
                        model_folders = self.col_model_folders
                    elif "PT" in folder_path:
                        model_folders = self.pt_model_folders
                    else:
                        raise Exception("Not found Petri net type from folder path")
                    for model_folder in self.model_folders_for_exam:
                        option = self.create_single_option(folder_path, category, search_strategy, model_folder)
                        all_options.append(option)

        return all_options

    def get_options(self):
        while not self.choose_directory_category_search_type() and not self.all_options:
            self.choose_directory_category_search_type()

        with open("theme.txt", mode='w') as file:
            file.write(str(self.current_theme))

        if not self.all_options:
            self.choose_tests_and_graph_type()

            model_folder = self.results_dir.split("\\")[-1]
            options = Options(
                result_dir=self.results_dir + self.chosen_directory,
                graph_dir=os.path.join(os.path.dirname(__file__), f"..\\graphs\\{self.chosen_directory}"),
                results_to_plot=self.results,
                category=self.category,
                folder=self.folder,
                test_names=[os.path.split(os.path.splitext(csv)[0])[1] for csv in self.results],
                chosen_graphs=self.graph_names,
                read_results=[],
                do_consistency_check=bool(self.do_consistency_check),
                enable_graphs=self.enable_graphs,
                debug=bool(self.debug),
                unique_results=bool(self.unique_results),
                petri_net_type=self.petri_net_type,
                all_options=False,
                search_strategy=self.search_strategy,
                base_name=self.base_name,
                overwrite=self.overwrite,
                folder_name=self.folder,
                model_folder=model_folder,
                chosen_directory=self.chosen_directory
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
            if self.only_one_test_setup:
                print(f"Doing absolutely everything for: {self.folder}")
            else:
                print(f"Doing absolutely everything")
            return self.create_all_options()
