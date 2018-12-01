import sys
sys.path.append('..')
import graphify

if __name__ == "__main__":
    path = "./"
    gg = graphify.Graphify(path, 10, 0)
    gg.process_section(1)


