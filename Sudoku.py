
import cv2
import numpy as np
import os

def perspective_transform(image, corners):
    def order_corner_points(corners):
       # Tách các góc thành các điểm riêng lẻ của bàn cả bàn cờ
        #  0 - top-right
        #  1 - top-left
        #  2 - bottom-left
        #  3 - bottom-right
        corners = [(corner[0][0], corner[0][1]) for corner in corners]
        top_r, top_l, bottom_l, bottom_r = corners[0], corners[1], corners[2], corners[3] 
        return (top_l, top_r, bottom_r, bottom_l)

    # Thứ tự các điểm theo chiều kim đồng hồ
    ordered_corners = order_corner_points(corners)
    top_l, top_r, bottom_r, bottom_l = ordered_corners

    # Xác định chiều rộng của hình ảnh mới là khoảng cách tối đa giữa
    # tọa độ x (dưới cùng bên phải và dưới cùng bên trái) hoặc 
    # (trên cùng bên phải và trên cùng bên trái)
    width_A = np.sqrt(((bottom_r[0] - bottom_l[0]) ** 2) + ((bottom_r[1] - bottom_l[1]) ** 2))
    width_B = np.sqrt(((top_r[0] - top_l[0]) ** 2) + ((top_r[1] - top_l[1]) ** 2))
    width = max(int(width_A), int(width_B))

    # Xác định chiều cao của hình ảnh mới là khoảng cách tối đa giữa 
    # tọa độ y (trên cùng bên phải và dưới cùng bên phải) hoặc 
    # (trên cùng bên trái và dưới cùng bên trái)
    height_A = np.sqrt(((top_r[0] - bottom_r[0]) ** 2) + ((top_r[1] - bottom_r[1]) ** 2))
    height_B = np.sqrt(((top_l[0] - bottom_l[0]) ** 2) + ((top_l[1] - bottom_l[1]) ** 2))
    height = max(int(height_A), int(height_B))

    # Xây dựng các điểm mới để có được chế độ xem ảnh từ trên xuống trong
    # top_r, top_l, bottom_l, bottom_r order
    dimensions = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], 
                    [0, height - 1]], dtype = "float32")

    # Convert to Numpy format
    ordered_corners = np.array(ordered_corners, dtype="float32")

    # Tìm ma trận biến đổi phối cảnh
    matrix = cv2.getPerspectiveTransform(ordered_corners, dimensions)

    # Trả về hình ảnh sau khi chuyển đổi
    return cv2.warpPerspective(image, matrix, (width, height))

image = cv2.imread('sudoku-original.jpg') # Đọc ảnh
original = image.copy() # Copy 1 ảnh khác
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # chuyển ảnh gray
blur = cv2.medianBlur(gray, 3) # Làm nét ảnh 

thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,3) #Chuyển ảnh qua binary
cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Tìm đường viền
cnts = cnts[0] if len(cnts) == 2 else cnts[1]   
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)  # Sắp xếp đa giac từ lớn đến nhỏ
for c in cnts: # lấy đa giác đầu tiên và có chu vi lớn nhất
    peri = cv2.arcLength(c, True) # Chu vi đa giác
    approx = cv2.approxPolyDP(c, 0.015 * peri, True)  # Tạo đa giác khác xấp xỉ vơi đa giác ban đầu tronh bài này là tứ giác với tọa độ 4 đỉnh
    transformed = perspective_transform(original, approx) # Gọi hàm đã tạo từ trước
    break


grid  =  cv2.cvtColor(transformed,cv2.COLOR_BGR2GRAY)
grid = cv2.medianBlur(grid, 3) # Làm nét ảnh 
grid = cv2.adaptiveThreshold(grid,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,3) #Chuyển ảnh qua binary
#cv2.imshow('grid', grid)
cv2.imwrite('output.jpg',grid)  #Lưu ảnh như yêu cầu đề bài

# Phần cắt từng ô vuông nhỏ trong sudoku và nhận diện có chữ số trong ô vuông hay không ##############
edge_h = np.shape(grid)[0] # Lấy chiều cao của bàn cờ
edge_w = np.shape(grid)[1] # Lấy chiều rộng của bàn cờ
celledge_h = edge_h // 9 # Chiều cao của mỗi ô vuông nhỏ trong bàn cờ
celledge_w = edge_w // 9  # Chiều dài của mỗi ô vuông nhỏ (Vì lấy gần đúng nên chiều dài và cao không bằng nhau trong ô vuông)

tempgrid = [] 
for i in range(celledge_h+6, edge_h + 1, celledge_h): # cho vòng lặp ma trận của ảnh đã cắt của mỗi ô vuông
    for j in range(celledge_w+1, edge_w + 1, celledge_w):
        rows = grid[i - celledge_h:i]
        tempgrid.append([rows[k][j - celledge_w:j] for k in range(len(rows))])
        
        
finalgrid = []
for i in range(0, len(tempgrid) - 8, 9):
    finalgrid.append(tempgrid[i:i + 9])

# Xử lý xác nhận xem trong ô vuông có số hay không
f = open('output.txt','w')
for i in range(9):
    for j in range(9):
        check = False
        finalgrid[i][j] = np.array(finalgrid[i][j])
        blur = cv2.GaussianBlur(finalgrid[i][j],(5,5),0)
        thresh = cv2.adaptiveThreshold(blur,255,1,1,11,2)
        contours, hierarchy  = cv2.findContours(image=thresh,mode = cv2.RETR_TREE,method=cv2.CHAIN_APPROX_NONE) #Hàm dùng để xác định khoảng ô chứa số
        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt) # Lấy tọa đồ, dài và rộng của các các ô vuông
            if(h > 20 and h < 30 and w > 11): # Mỗi số trong bàn cờ sudoku sau khi xử lý sẽ rơi vào khoảng chiều cao 20 đến 30 và rộng > 11
                f.write('   X   ') # Xuất file text như yêu cầu đề bài
                check = True
        if (j == 8):
            if(check == True):   
                f.write('\n')
            else:
                f.write('   -\n')
            continue
        if check == False:
            f.write('   -   ')
        
cv2.waitKey()