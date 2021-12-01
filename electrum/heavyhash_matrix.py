import math

debug = False

# def generate_heavyhash_matrix(matrix_seed: int) -> np.ndarray:
#     generator = pure_prng(matrix_seed, 'xoshiro256++')
#     result = np.arange(64 * 64).reshape((64, 64))
# 
#     while True:
#         for i in range(64):
#             for j in range(0, 64, 16):
#                 value = generator.source_random_number()
#                 for shift in range(16):
#                     result[i][j + shift] = (value >> (4 * shift)) & 0xF
# 
#         # Emulate do...while behavior =)
#         if (not is_4bit_precision(result)) or (not is_full_rank(result)):
#             # start loop again
#             continue
#         # End generating matrix
#         break
# 
#     return result
# 
# 
def is_4bit_precision(m: [[int]]) -> bool:
    for i in range(64):
        for j in range(64):
            if m[i][j] < 0 or m[i][j] > 0xF:
                if (debug):
                    print(f'Matrix is not 4bit precision at pos [{i}, {j}]: {m[i][j]}')
                return False
    return True


# def is_full_rank(m: np.ndarray) -> bool:
#     return np.linalg.matrix_rank(m) == 64

#def generate_heavyhash_matrix(matrix_seed):
#    xoshiro_seed_bytes_count = math.ceil(256 / 8)
#    seed_bytes = matrix_seed.to_bytes(xoshiro_seed_bytes_count, byteorder = 'little')
#    return generate_heavyhash_matrix_internal(xoshiro256pp_seeding(seed_bytes))

def generate_heavyhash_matrix(matrix_seed):
    hashStr = '0x'
    for b in matrix_seed:
        hashStr += "%0.2X" % b

    if (debug):
        print(f'Matrix generation seed: 0x{hashStr}')
    return generate_heavyhash_matrix_internal(xoshiro256pp_seeding(matrix_seed))

def generate_heavyhash_matrix_internal(s):
    matrix = []
    check_matrix = []

    for i in range(64):
        matrix.append([])
        check_matrix.append([])
        for j in range(64):
            matrix[i].append(0)
            check_matrix[i].append(0)

    for i in range(0, 64):
        for j in range(0, 64, 16):
            value, s = xoshiro256pp(s)
            for shift in range(0, 16):
                matrix[i][j + shift] = (value >> (4 * shift)) & 0xF
                check_matrix[i][j + shift] = matrix[i][j + shift]

    #rank = rankMatrix(check_matrix).rankOfMatrix(check_matrix)
    if (not is_4bit_precision(matrix)) or MatrixRank(check_matrix) != 64:
        generate_heavyhash_matrix_internal(s)

    return matrix

class rankMatrix():
    def __init__(self, matrix):
        self.rows = len(matrix)
        self.cols = len(matrix[0])

    def swap(self, matrix, row1, row2, col):
        for i in range(col):
            temp = matrix[row1][i]
            matrix[row1][i] = matrix[row2][i]
            matrix[row2][i] = temp

    def rankOfMatrix(self, matrix):
        rank = self.cols
        for row in range(0, rank, 1):

            if matrix[row][row] != 0:
                for col in range(0, self.rows, 1):
                    if col != row:

                        multiplier = (matrix[col][row] /
                                      matrix[row][row])
                        for i in range(rank):
                            matrix[col][i] -= (multiplier *
                                               matrix[row][i])
            else:
                reduce = True
                for i in range(row + 1, self.rows, 1):

                    if matrix[i][row] != 0:
                        self.swap(matrix, row, i, rank)
                        reduce = False
                        break
                if reduce:
                    rank -= 1
                    for i in range(0, self.rows, 1):
                        matrix[i][row] = matrix[i][rank]
                row -= 1
        return (rank)

def swapRows(A,row1,row2):                        #FUNCTION TO SWAP TWO ROWS OF A MATRIX A
	A[row2],A[row1]=A[row1],A[row2]
	return A

def Row_Transformation(A,x,row1,row2):            #FUNCTION TO PERFORM ROW TRANSFORMATION ON ROWS OF A MATRIX
	k=len(A[row2])
	for m in range(k):
		A[row2][m]=A[row2][m] + A[row1][m]*x
	return A

def MatrixRank(A):
	colnum=len(A[0])
	rownum=len(A)
	Rank=min(colnum,rownum)                       #RANK IS THE MINIMUM OF colnum AND rownum
	if (rownum>colnum):
		list1=[]
		for i in range(colnum):
			list2=[]
			for j in range(rownum):
				list2.append(A[i][j])
			list1.append(list2)
		list1=list2
		colnum,rownum=rownum,colnum

	for l in range(Rank):
		if(A[l][l]!=0):
			for n in range(l+1,rownum):
				A=Row_Transformation(A,-(A[n][l]//A[l][l]),l,n)  #INVOKING Row_Transformation FUNCTION
		else:
			flag1=True
			for o in range(l+1,rownum):
				if(A[o][l]!=0):
					A=swapRows(A,l,o)
					flag1=False
					break
			if(flag1):
				for i in range(rownum):
					A[i][l],A[i][Rank-1]=A[i][Rank-1],A[i][l]
			rownum=rownum-1
		c=0
		for z in A:
			if(z==[0]*colnum):
				c=c+1

		if debug:
				print(Rank - c)
	return Rank-c

def get_uint64(data, pos):
    ptr = pos*8
    uint64 = data[ptr] | (data[ptr+1] << 8) | (data[ptr+2] << 16) | (data[ptr+3] << 24) | (data[ptr+4] << 32) |\
             (data[ptr+5] << 40) | (data[ptr+6] << 48) | (data[ptr+7] << 56)

    return uint64

""" XOSHIRO256++ ALGORITHM
    A pseudo random number generator used in Heavy Hashing for
    matrix generation """
def rol64(x, k):
    return ( (x << k) & 0xFFFFFFFFFFFFFFFF ) | ( (x >> (64 - k)) & 0xFFFFFFFFFFFFFFFF )

def xoshiro256pp_seeding(seed):
    s = [0, 0, 0, 0]
    for i in range(4):
        s[i] = get_uint64(seed, i)
    return s

def xoshiro256pp(s):
    result = (rol64((s[0]+ s[3]) & 0xFFFFFFFFFFFFFFFF, 23) + s[0]) & 0xFFFFFFFFFFFFFFFF
    t = (s[1] << 17) & 0xFFFFFFFFFFFFFFFF

    s[2] ^= s[0]
    s[3] ^= s[1]
    s[1] ^= s[2]
    s[0] ^= s[3]

    s[2] ^= t
    s[3] = rol64(s[3] & 0xFFFFFFFFFFFFFFFF, 45)

    return result, s

test_matrix = [
        [5,9,8,5,5,2,7,10,11,10,5,3,6,6,6,13,12,2,3,15,0,1,0,7,4,7,12,2,2,4,2,2,8,2,12,1,15,4,12,11,13,13,2,10,1,9,8,3,6,14,6,13,13,5,2,6,0,0,5,10,13,5,13,13],
        [7,10,2,7,11,8,3,13,5,0,9,1,8,1,10,14,0,13,15,9,15,2,7,8,10,7,7,2,2,1,10,3,6,4,9,12,0,9,8,0,5,4,11,4,2,7,13,12,5,5,9,12,11,11,7,11,0,1,0,14,9,8,12,5],
        [10,0,0,2,1,14,14,10,12,8,13,6,13,11,7,13,9,8,1,5,5,8,9,14,14,1,11,3,13,4,0,15,5,7,0,3,2,10,15,1,3,5,14,10,8,6,2,2,6,5,0,8,15,9,2,5,3,7,10,5,4,13,0,11],
        [14,2,14,0,7,14,8,8,12,7,3,14,4,5,3,12,14,8,14,8,5,4,4,6,10,0,2,11,2,3,8,13,12,0,3,9,6,0,11,4,10,2,12,12,11,6,12,0,14,3,10,5,11,3,15,5,15,2,15,11,10,11,4,9],
        [6,3,3,6,3,1,10,12,15,1,2,11,5,14,14,8,4,15,7,1,10,11,6,15,2,14,2,0,1,15,1,8,9,6,6,2,8,5,5,0,0,8,12,8,4,1,0,4,9,0,4,7,4,7,14,5,8,0,14,13,12,11,4,10],
        [8,14,15,15,6,9,7,8,2,1,7,6,12,15,5,2,9,3,14,9,15,13,10,0,2,1,6,3,5,13,3,15,10,14,11,8,12,6,11,5,13,6,11,2,5,4,6,4,9,1,7,0,13,2,0,5,6,10,9,2,10,11,13,14],
        [0,3,2,13,13,13,7,9,11,2,5,11,7,10,2,1,13,11,4,1,10,15,11,15,3,15,15,7,14,3,5,6,9,8,10,12,4,14,13,0,8,4,2,10,3,13,8,5,3,2,5,11,3,11,11,10,8,5,0,13,7,14,3,7],
        [4,7,8,1,8,12,10,10,12,5,5,9,4,0,14,13,2,4,1,8,11,2,1,7,12,13,3,7,1,5,5,5,14,7,10,12,3,2,9,10,11,14,11,13,4,3,8,8,4,13,8,4,3,9,3,14,2,2,10,4,15,0,2,10],
        [0,4,5,11,6,5,6,8,5,8,0,10,9,6,14,0,4,9,5,11,14,9,15,9,12,14,15,6,2,1,1,6,6,7,4,13,11,5,4,9,2,12,8,9,12,9,15,6,2,6,12,5,12,5,3,12,7,15,9,1,14,1,5,9],
        [4,11,3,5,7,10,5,7,5,13,6,15,0,3,13,8,1,15,12,0,15,1,13,9,15,11,2,0,4,8,1,4,0,8,9,9,9,2,2,2,15,2,15,3,12,13,0,11,13,1,7,5,15,3,1,7,0,0,4,8,9,9,11,14],
        [12,12,11,5,13,13,4,12,1,1,0,3,3,4,7,0,8,6,9,12,15,7,11,7,3,1,2,3,8,14,5,0,12,4,15,10,13,5,6,1,13,7,2,1,13,0,15,7,4,4,7,11,10,5,2,9,1,8,0,10,14,8,3,4],
        [13,11,14,10,1,6,15,10,5,14,13,4,13,6,1,14,7,14,6,6,8,13,4,5,5,2,8,9,9,13,7,8,12,4,4,1,2,10,12,6,8,0,3,13,12,10,11,13,9,4,0,3,5,6,1,13,3,7,13,5,5,7,8,10],
        [10,15,2,14,2,6,5,13,4,2,5,2,11,5,5,1,2,4,5,9,9,14,11,2,10,10,13,2,8,5,14,15,6,6,12,11,9,14,1,12,15,1,0,9,3,8,9,0,12,4,12,3,0,6,1,7,14,14,3,8,11,11,4,4],
        [14,14,4,9,11,6,10,0,14,9,0,5,9,15,6,6,14,7,12,10,5,7,0,10,5,10,5,15,8,1,2,11,12,11,13,8,11,13,13,5,9,14,13,3,6,3,0,14,11,2,15,9,7,7,3,8,12,11,13,14,7,7,7,0],
        [8,2,8,10,11,6,12,2,1,1,4,9,9,9,4,7,10,3,10,6,9,13,13,14,8,3,0,9,14,4,6,10,6,4,15,13,13,12,15,15,0,5,4,7,10,14,7,5,12,10,6,5,6,11,12,11,5,9,1,13,15,10,9,14],
        [6,4,9,4,4,3,10,3,10,8,7,15,1,2,4,5,4,14,1,12,11,10,3,4,1,7,8,12,12,12,14,10,12,10,15,12,9,7,6,7,5,3,5,7,0,2,13,1,15,14,15,15,2,14,2,8,0,4,2,7,11,7,11,4],
        [2,10,5,11,5,0,3,3,2,1,14,8,15,5,7,1,13,5,11,6,1,6,9,12,6,15,3,14,4,14,13,11,8,1,15,4,1,10,13,10,15,10,11,2,7,8,6,10,12,8,3,0,3,0,2,1,10,7,5,8,10,14,11,12],
        [12,8,3,13,14,6,15,13,3,7,13,3,3,1,15,3,10,7,13,9,8,1,3,6,9,1,4,8,8,6,14,9,3,9,7,4,1,8,2,0,9,9,8,11,15,11,6,4,9,0,11,3,0,4,9,14,10,3,3,8,15,15,10,10],
        [9,10,13,12,14,9,15,5,15,1,11,8,10,7,10,10,12,10,9,6,3,0,12,11,6,0,4,9,14,15,7,10,7,1,8,15,3,10,10,13,3,1,5,10,1,9,6,11,14,2,9,0,3,7,6,11,8,0,7,4,11,3,12,4],
        [12,8,8,3,0,14,5,8,2,7,10,14,15,15,0,11,14,6,2,5,1,15,0,15,15,11,15,1,10,13,6,7,4,8,1,9,11,3,0,15,10,4,11,11,7,14,4,12,2,9,3,10,2,7,6,0,4,9,4,0,10,8,8,12],
        [10,10,10,6,1,0,2,9,1,1,13,2,3,7,3,5,13,2,13,8,7,2,0,0,11,11,0,8,10,7,7,13,7,13,9,12,7,5,8,4,15,1,14,5,12,15,2,9,3,10,12,8,2,0,2,13,8,10,8,13,4,6,8,9],
        [1,11,12,3,4,12,12,12,1,2,0,4,14,7,1,9,13,11,14,15,3,7,3,0,1,3,3,5,2,1,4,8,14,11,3,4,3,7,9,15,8,3,0,15,4,0,4,2,8,14,14,1,3,7,12,12,4,7,4,2,3,4,1,1],
        [1,14,7,9,12,8,14,6,11,8,2,13,0,8,8,15,13,7,1,6,4,5,2,12,4,8,0,13,11,13,0,6,5,0,0,6,9,2,11,11,1,0,9,12,1,15,15,0,7,6,4,4,6,14,4,2,1,14,4,11,3,9,8,15],
        [10,11,1,8,7,9,7,13,7,1,1,10,1,8,6,12,12,13,0,3,8,13,5,13,10,0,12,1,0,8,9,15,3,6,5,0,11,9,15,14,3,11,7,15,7,3,14,7,1,5,2,1,3,2,14,8,13,3,4,15,0,6,1,11],
        [8,14,14,8,9,8,8,5,14,7,7,10,12,0,6,3,5,3,11,14,9,8,1,7,7,4,1,8,4,11,3,4,13,3,3,2,13,4,14,12,7,10,3,13,1,7,1,15,0,5,6,7,4,8,4,4,12,15,6,11,15,13,10,13],
        [0,5,8,13,10,2,7,8,15,8,1,7,12,10,3,5,2,5,9,10,12,0,10,3,10,8,4,2,0,5,9,13,7,12,13,14,7,1,11,0,7,5,0,1,15,11,14,4,4,11,5,14,9,15,12,2,13,1,4,2,10,4,12,13],
        [15,12,9,2,2,13,1,13,2,0,6,4,0,12,15,4,10,3,10,3,15,0,1,15,15,6,0,14,14,11,1,6,1,6,3,10,11,0,11,9,6,7,15,15,9,13,9,5,12,3,13,6,11,10,11,9,4,7,5,5,6,3,2,12],
        [8,13,7,10,13,2,9,0,1,13,15,7,2,9,6,5,10,5,10,11,6,11,1,12,15,3,10,1,15,0,7,2,3,5,4,2,4,6,15,11,7,5,8,0,8,3,15,15,12,13,6,1,1,3,8,4,1,6,14,4,13,7,4,2],
        [9,4,1,2,12,9,7,0,2,14,13,7,7,1,6,6,8,2,2,14,1,8,12,1,10,7,9,8,6,0,14,5,2,1,5,4,13,0,11,1,1,1,0,6,5,2,1,1,9,10,7,7,11,0,14,6,6,5,13,15,5,9,2,14],
        [7,13,13,14,2,0,6,10,5,14,5,15,0,5,1,0,1,10,1,7,14,7,14,4,13,10,2,8,10,5,0,5,10,12,1,8,14,10,13,12,7,11,9,6,9,9,10,4,9,0,12,2,14,1,8,6,8,12,2,10,7,15,0,7],
        [14,8,6,7,2,9,14,0,11,0,8,2,8,2,13,12,2,3,12,6,8,14,7,6,5,13,4,13,11,10,2,2,12,0,2,12,4,13,2,4,7,1,15,9,12,13,9,8,13,14,8,1,6,9,8,4,5,9,7,10,5,4,5,9],
        [11,13,13,11,6,11,10,8,9,3,8,1,14,1,9,0,11,7,3,15,13,6,1,5,3,7,11,14,1,13,6,14,9,15,13,13,10,2,13,2,8,3,0,0,7,5,12,1,8,8,13,15,14,11,8,9,13,6,11,4,1,12,15,12],
        [8,7,9,12,7,12,11,7,0,0,1,1,11,14,5,3,1,12,0,2,8,1,14,0,9,9,8,13,2,11,1,2,8,10,12,15,3,13,15,1,13,7,4,2,8,11,2,11,3,15,7,6,6,5,1,0,7,8,5,5,9,4,12,5],
        [5,0,15,9,15,4,9,15,12,12,2,14,1,1,6,14,2,6,11,7,9,1,8,11,2,12,5,14,15,11,10,5,15,3,15,9,2,0,14,12,1,6,15,5,15,15,5,10,1,1,2,11,13,15,4,5,5,1,14,12,6,2,6,0],
        [4,10,13,1,7,0,4,12,9,8,0,3,2,5,10,9,6,0,2,15,1,0,11,7,3,2,12,6,13,8,11,0,12,0,7,8,11,1,12,7,10,7,15,10,8,6,3,14,15,6,11,13,13,6,15,4,1,9,3,4,3,7,4,11],
        [8,9,10,1,8,11,9,12,0,1,6,6,5,12,0,6,15,14,12,4,9,6,9,7,0,5,12,6,11,14,1,11,6,13,11,12,11,10,0,7,2,12,10,14,3,15,7,7,6,0,7,8,11,1,12,6,0,15,13,14,9,11,8,7],
        [2,9,12,9,7,6,7,2,5,5,7,8,15,1,9,13,6,11,14,11,4,14,5,12,3,7,9,6,7,8,15,5,15,12,13,8,4,12,7,3,7,13,13,15,13,11,10,9,8,6,4,12,8,15,8,9,12,9,3,8,2,5,8,1],
        [5,8,1,4,7,12,3,5,13,10,3,8,10,5,7,8,13,5,5,10,7,3,14,0,4,3,2,10,15,0,9,8,13,4,0,15,9,6,2,8,11,1,6,0,10,13,14,2,10,4,7,7,0,6,1,8,13,13,10,12,4,12,15,10],
        [0,4,5,11,1,11,4,3,7,9,10,2,10,9,14,10,10,9,6,4,8,6,2,13,15,1,10,9,8,5,11,13,9,9,14,3,8,12,6,13,10,10,6,3,0,12,8,4,7,5,9,13,6,10,3,5,12,2,7,7,0,12,15,6],
        [9,3,8,7,2,3,10,10,11,15,8,8,2,8,6,5,15,12,4,3,8,7,0,0,1,2,15,0,5,3,9,2,10,10,13,0,13,7,10,6,10,10,8,0,8,11,12,3,6,4,11,13,4,8,10,12,3,0,1,3,12,2,2,9],
        [15,12,6,1,9,6,11,0,3,12,4,2,3,10,10,1,10,12,10,3,6,12,15,15,10,4,13,12,8,15,5,10,10,8,15,9,10,11,13,9,0,10,10,1,3,6,10,11,14,15,12,11,15,6,9,5,15,5,4,14,12,15,2,2],
        [8,11,9,8,3,12,15,6,10,10,7,0,6,11,6,7,1,9,3,15,4,11,5,11,12,13,8,3,12,2,15,5,5,2,3,9,1,7,12,1,12,10,2,11,6,10,15,3,14,15,13,8,5,9,15,7,11,15,9,12,7,9,6,8],
        [6,14,6,6,12,9,3,11,14,5,2,9,10,6,7,4,6,15,4,14,8,5,4,10,10,1,14,7,13,13,0,1,15,0,13,5,1,9,12,4,4,6,3,4,2,13,10,7,3,2,8,10,11,8,11,10,7,6,13,15,11,14,8,7],
        [11,6,6,6,1,1,0,0,3,0,9,7,0,8,15,13,9,10,3,9,11,10,12,12,6,4,14,5,7,15,5,8,12,4,1,13,7,14,1,8,5,8,7,7,12,0,1,7,9,15,2,6,4,13,2,0,13,15,7,5,14,0,7,3],
        [8,5,15,12,2,2,0,15,9,14,10,13,13,3,11,1,4,8,5,5,3,12,2,14,9,1,9,6,13,2,9,2,15,12,8,14,12,10,3,14,6,6,6,10,10,5,5,6,2,1,1,1,4,14,6,3,4,4,1,2,15,1,12,5],
        [12,9,9,2,7,13,14,5,3,12,0,7,2,6,14,5,8,3,5,1,8,9,10,7,8,15,13,6,0,12,15,9,8,9,1,15,3,5,1,2,11,4,9,12,4,14,7,12,14,7,13,6,15,5,6,15,2,2,0,9,11,5,8,13],
        [7,13,9,4,14,10,0,7,0,7,7,4,10,12,3,15,3,13,2,0,11,3,11,14,10,15,7,15,2,1,12,2,12,12,11,9,14,6,12,7,15,3,1,2,3,9,4,0,10,10,14,5,5,3,10,6,3,3,13,12,2,11,11,2],
        [1,14,9,13,8,4,12,10,11,1,11,12,5,0,1,4,1,0,15,3,11,4,14,14,1,1,9,1,6,14,1,10,4,5,12,10,6,5,9,1,3,8,4,7,2,11,8,5,6,4,9,8,5,12,1,11,15,11,0,7,13,1,13,3],
        [13,9,8,15,8,9,13,8,11,2,3,11,4,3,6,15,4,0,12,10,13,13,6,7,15,1,6,11,2,14,11,8,0,10,2,13,2,9,8,11,12,2,10,9,6,1,10,4,12,1,12,12,1,15,14,10,12,5,7,4,12,4,8,12],
        [5,0,12,7,8,15,14,11,8,11,1,12,10,9,11,7,10,12,5,10,7,6,1,6,10,11,9,10,8,6,14,7,12,6,11,6,12,0,3,4,2,11,5,9,2,2,10,3,14,5,11,4,5,11,15,10,6,9,13,2,11,13,3,3],
        [6,4,9,8,6,10,1,6,9,2,4,7,3,15,3,0,0,1,2,8,4,9,10,9,4,0,4,5,7,1,11,12,6,14,6,10,8,0,4,1,4,6,14,9,7,3,1,12,3,2,5,8,13,1,7,3,11,3,3,15,8,9,4,11],
        [11,5,12,11,8,7,13,7,9,3,10,10,6,13,1,14,15,11,2,0,1,8,6,12,6,10,12,9,4,12,8,13,8,10,14,8,10,8,8,14,0,4,11,10,15,1,8,0,1,15,11,2,9,3,10,14,14,6,11,2,13,5,6,9],
        [1,6,5,11,10,13,14,2,5,2,9,15,13,5,12,0,12,7,8,14,15,2,4,8,12,5,13,9,13,12,11,4,1,3,11,0,8,15,0,4,12,6,12,3,13,11,0,5,4,8,10,11,12,10,11,5,15,10,8,0,1,10,3,6],
        [13,8,15,5,12,9,12,4,8,5,10,4,15,13,9,8,8,3,7,14,12,2,11,8,7,9,2,6,13,9,4,11,15,8,8,4,1,9,4,12,11,9,13,10,11,11,9,15,2,12,12,15,13,4,14,8,1,15,10,7,14,6,11,9],
        [15,13,6,1,10,3,4,6,0,5,8,13,6,2,12,15,4,9,1,0,8,13,5,0,9,13,0,7,10,15,10,15,3,2,15,9,5,6,2,8,12,7,10,7,3,14,14,1,11,0,4,1,4,12,11,10,4,5,13,6,6,5,4,8],
        [10,0,13,13,2,5,6,8,3,4,7,12,15,0,12,5,2,6,1,1,0,8,14,10,9,8,4,11,8,3,8,11,5,8,15,3,11,1,10,13,14,7,13,2,2,7,5,11,6,11,1,12,9,6,6,2,1,9,10,1,15,1,7,13],
        [4,13,8,5,11,7,5,5,3,10,2,9,5,9,8,0,5,7,2,1,4,8,13,11,14,5,10,13,11,13,2,11,6,7,9,13,5,6,0,13,12,11,8,14,2,2,13,11,8,11,5,8,6,5,2,3,4,0,11,13,12,10,9,11],
        [2,6,5,2,12,12,5,2,6,15,11,1,7,1,3,13,14,6,3,10,8,10,6,7,2,7,12,8,10,11,10,12,2,9,1,6,11,2,8,2,4,9,11,3,12,2,15,4,6,4,12,10,5,0,2,4,11,0,11,5,12,7,8,13],
        [12,5,13,12,12,13,1,3,5,0,4,2,11,10,15,14,6,1,11,4,4,6,14,1,6,9,4,4,2,3,6,9,10,3,8,9,10,0,13,2,1,2,5,4,2,8,2,12,14,8,8,7,14,12,7,1,6,10,13,6,6,12,11,10],
        [11,12,1,15,13,0,3,2,0,6,1,12,12,1,4,12,4,0,6,15,5,7,13,9,7,13,2,3,10,5,13,2,11,10,12,13,12,2,12,8,14,7,9,11,3,0,9,1,6,7,11,6,6,4,9,3,7,10,9,10,4,4,0,1],
        [8,10,7,4,13,0,12,14,13,4,13,4,6,10,2,7,5,7,5,14,8,7,8,4,10,12,8,10,1,10,11,2,13,12,13,3,5,9,11,12,14,4,7,15,13,3,14,8,4,1,15,1,7,12,14,12,1,7,15,5,0,2,8,10],
        [12,3,3,15,15,7,15,1,7,1,0,7,6,0,10,6,15,2,15,10,14,12,6,5,3,1,14,3,3,11,6,10,11,4,10,7,7,12,2,2,6,0,11,3,7,15,10,12,1,10,6,7,12,11,1,4,14,12,14,2,13,11,8,5],
        [7,13,3,9,15,13,0,12,11,10,14,6,11,5,3,14,7,3,9,1,13,2,10,2,5,3,14,12,3,14,7,15,15,7,3,4,3,6,5,4,5,0,8,3,1,1,6,6,7,1,3,11,2,7,0,11,12,10,3,11,12,13,7,3],
        [6,5,5,5,15,1,3,12,8,1,11,15,4,14,6,0,2,13,11,14,6,0,12,13,6,3,1,0,3,0,5,1,3,11,7,3,1,14,4,12,12,6,9,6,11,9,14,8,14,8,7,13,14,12,12,8,3,7,10,14,3,0,11,2]
]
test_seed = 0x4e9e3bed9971db8147a0b2a59bb4b4186fd8f9ca9bc70840d94db40c9791629e

if __name__ == '__main__':
    import sys

    print(f'Seed is correct: "{hex(test_seed)}" == "0x4e9e3bed9971db8147a0b2a59bb4b4186fd8f9ca9bc70840d94db40c9791629e"? ', hex(test_seed) == "0x4e9e3bed9971db8147a0b2a59bb4b4186fd8f9ca9bc70840d94db40c9791629e")

    matrix = generate_heavyhash_matrix(test_seed)
    print('Generated matrix: [')
    for i in range(0, 64):
        print('\t[', end='')
        for j in range(0, 64):
            print(f'{matrix[i][j]},', end='') if j != 63 else print(f'{matrix[i][j]}', end='')
        print('],')
    print(']')

    for i in range(0, 64):
        for j in range(0, 64):
            if (test_matrix[i][j] != matrix[i][j]):
                print(f'Generated matrix is incorrect at cell [{i}, {j}]. Expected: {test_matrix[i][j]}, but got: {matrix[i][j]}')
                sys.exit(1)

    print('Matrix test - succeed')

