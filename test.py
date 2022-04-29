#
# This module is used only for testing Maze and SearchableMaze classes.
#

import random
from colorama import Fore, Back, Style

from maze import Maze, Block
from searchablemaze import Node, SearchableMaze

# For plotting
import matplotlib.pyplot as plt # for visualization

def test(start, end):
    maze_size = (40, 20)

    maze = Maze()
    maze.generate(maze_size, start, end)

    s_maze = SearchableMaze(maze)

    novel_results = s_maze.find_novel_path(start, end)
    bi_results = s_maze.find_bidirectional_path(start, end)

    maze.draw_path(novel_results['paths'][0], Block.HIGHLIGHT_2)
    maze.draw_path(novel_results['paths'][1], Block.HIGHLIGHT_3)

    maze.print()

    maze.draw_path(novel_results['paths'][0], Block.PATH)
    maze.draw_path(novel_results['paths'][1], Block.PATH)

    maze.draw_path(bi_results['paths'][0], Block.HIGHLIGHT_1)
    maze.draw_path(bi_results['paths'][1], Block.HIGHLIGHT_1)

    maze.print()

    novel_path_length = 0
    for path in novel_results["paths"]:
        novel_path_length += len(path)

    bi_path_length = 0
    for path in bi_results["paths"]:
        bi_path_length += len(path)

    print(Style.BRIGHT, "Iterations to find goal using novel approach:", novel_results['iterations'], Style.RESET_ALL)
    print(Fore.CYAN, "Time taken in seconds (novel):",round(novel_results["duration"],5), Fore.RESET)
    print(Fore.BLUE, "Total path length (novel):", novel_path_length, "\n", Fore.RESET)

    print(Style.BRIGHT, "Iterations to find goal using traditional approach:", bi_results['iterations'], Style.RESET_ALL)
    print(Fore.CYAN, "Time taken in seconds (traditional):", round(bi_results["duration"],5), Fore.RESET)
    print(Fore.BLUE, "Total path length (traditional):", bi_path_length, "\n", Fore.RESET)

    return [
        [bi_path_length, bi_results["duration"],bi_results["iterations"]],
        [novel_path_length, novel_results["duration"],novel_results["iterations"]],
    ]

def iterative_test(iter_count):

    durations_novel = []
    durations_bi = []

    iterations_novel = []
    iterations_bi = []

    path_lengths_novel = []
    path_lengths_bi = []

    for i in range(0, iter_count):

        start = (0, 0)
        end = (39, 19)

        results = test(start, end)

        path_lengths_bi.append(results[0][0])
        durations_bi.append(results[0][1])
        iterations_bi.append(results[0][2])

        path_lengths_novel.append(results[1][0])
        durations_novel.append(results[1][1])
        iterations_novel.append(results[1][2])

    avg_path_length_bi = sum(path_lengths_bi) / iter_count
    avg_duration_bi = round(sum(durations_bi) / iter_count,5)
    avg_iterations_bi = sum(iterations_bi) / iter_count

    avg_path_length_novel = sum(path_lengths_novel) / iter_count
    avg_duration_novel = round(sum(durations_novel) / iter_count,5)
    avg_iterations_novel = sum(iterations_novel) / iter_count

    print("\n\n")
    print(Back.WHITE, Fore.BLACK, f"Test over {iter_count} iterations:", Style.RESET_ALL, "\n")
    print(Style.BRIGHT, Fore.BLUE, f"Average path length:\n    traditional -> {avg_path_length_bi}\n    novel -> {avg_path_length_novel}\n", Style.RESET_ALL)
    print(Style.BRIGHT, f"Average runtime:\n    traditional -> {avg_duration_bi}\n    novel -> {avg_duration_novel}\n", Style.RESET_ALL)
    print(Style.BRIGHT, f"Average iterations:\n    traditional -> {avg_iterations_bi}\n    novel -> {avg_iterations_novel}\n", Style.RESET_ALL)

    return {
        "bi": {
            "path_lengths": path_lengths_bi,
            "durations": durations_bi,
            "iterations": iterations_bi
        },
        "novel": {
            "path_lengths": path_lengths_novel,
            "durations": durations_novel,
            "iterations": iterations_novel
        }
    }

def plot(a, b, title='', ylabel='', xlabel=''):
    plt.plot(a[1], label=a[0])
    plt.plot(b[1], label=b[0])

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    plt.legend(loc='best')
    plt.title(title)
    plt.show()

def avg(ls):
    return sum(ls) / len(ls)

def generate_averages(tests=10):
    durations_novel = []
    durations_bi = []

    iterations_novel = []
    iterations_bi = []

    path_lengths_novel = []
    path_lengths_bi = []
    
    for i in range(0,tests):
        results = iterative_test(20)

        durations_bi.append(avg(results['bi']['durations']))
        iterations_bi.append(avg(results['bi']['iterations']))
        path_lengths_bi.append(avg(results['bi']['path_lengths']))

        durations_novel.append(avg(results['novel']['durations']))
        iterations_novel.append(avg(results['novel']['iterations']))
        path_lengths_novel.append(avg(results['novel']['path_lengths']))

    return {
        "bi": {
            "path_lengths": path_lengths_bi,
            "durations": durations_bi,
            "iterations": iterations_bi
        },
        "novel": {
            "path_lengths": path_lengths_novel,
            "durations": durations_novel,
            "iterations": iterations_novel
        }
    }

def generate_plot(tests=10):
    durations_novel = []
    durations_bi = []

    iterations_novel = []
    iterations_bi = []

    path_lengths_novel = []
    path_lengths_bi = []

    for i in range(0,tests):
        results = generate_averages(5)

        durations_bi.append(avg(results['bi']['durations']))
        iterations_bi.append(avg(results['bi']['iterations']))
        path_lengths_bi.append(avg(results['bi']['path_lengths']))

        durations_novel.append(avg(results['novel']['durations']))
        iterations_novel.append(avg(results['novel']['iterations']))
        path_lengths_novel.append(avg(results['novel']['path_lengths']))

    plot(('Traditional Path Length',path_lengths_bi), ('Novel Path Length',path_lengths_novel),'Traditional v. Novel Path Length','Path Length', 'Test')
    plot(('Traditional Duration',durations_bi), ('Novel Duration',durations_novel),'Traditional v. Novel Duration', 'Duration (s)', 'Test')
    plot(('Traditional Iterations',iterations_bi), ('Novel Iterations',iterations_novel),'Traditional v. Novel Iterations', 'Search Iterations', 'Test')

generate_plot(10)