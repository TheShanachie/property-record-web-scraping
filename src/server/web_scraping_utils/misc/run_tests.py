import re, os, subprocess, tqdm, importlib, inspect
from typing import Callable
from termcolor import colored

def try_import_test(module_name: str) -> Callable:
    # Check whether one can import module, return None if any error.
    try:
        module = importlib.import_module(name=module_name)
        func = module.run_tests
        assert inspect.get_annotations(func)['return'] is bool
        return func
    except:
        return

# Get test module names and test functions
running_dir = '.'
test_dir_name_re = '^t{1}[0-9]+$'
valid_test_dir = lambda x: os.path.isdir(x) and re.fullmatch(test_dir_name_re, x) is not None
test_dir_names = list(filter(valid_test_dir, os.listdir(running_dir)))
zipped_tests = []
for test_dir_name in test_dir_names:
    test_method = try_import_test(test_dir_name)
    if test_method is not None:
        zipped_tests.append((test_dir_name, test_method))
    

# Run each test indevidually. (Update across threads later.)
zipped_results = []
print("Test Results:")
for test, method in zipped_tests:
    result = method()
    zipped_results.append((test, result))
    print(f"    Test {test}:", colored(result, 'red') if result is False else colored(result, 'green'))

# Get a list of pos and neg tests. Calculate the score (percentage positive)
passed = float(len([test for test, result in zipped_results if result]))
failed = float(len([test for test, result in zipped_results if not result]))
score = 0.0
if passed > 0:
    score = passed / (passed+failed)
   
# Print the overall score. 
print("Percent Passed:", colored(f'{score:.4f}', 'red') if score <= .5 else colored(f'{score:.4f}', 'green'))

    
    
