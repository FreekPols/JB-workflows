# testing with opdracht.ipynb

#  function to do the actual check for sol_check_1
def check_sol_1(func):
    
    array1 = np.array([-5, 0, 5])   # testarrays
    array2 = np.array([-3, 4, 2])

    result = func(array1, array2)   # use students function

    expected = array1 + array2      # expected result

    np.testing.assert_array_equal(result, expected)



# function to do the actual check for sol_check_2
def check_sol_2(func):
    
    array1 = np.array([-5, 0, 5])   # testarrays
    array2 = np.array([-3, 4, 2])

    result = func(array1, array2)   # use students function

    expected = array1 * array2      # expected result

    np.testing.assert_array_equal(result, expected)

# check("sol_check_2", check_sol_2, functions[1])    
# check("sol_check_1", check_sol_1, functions[0])