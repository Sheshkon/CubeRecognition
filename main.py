import cv2
import numpy as np
import colors
import position
from twophase import solve
import threading
from cube3d import RubiksCube


def show_scramble_2d(text=None, img=None):
    cv2.imshow(text, img)
    cv2.waitKey(0)


def create_cube(solution, start_position):
    game = RubiksCube(solution, start_position)
    game.run()


def find_solution(scramble):
    try:
        solution = solve(scramble)
    except:
        solution = 'not found'

    return solution


def create_scramble_board():
    scramble_image = np.zeros([512, 512, 3], dtype=np.uint8)
    scramble_image.fill(0)
    height, width, _ = scramble_image.shape
    for i in range(4):
        cv2.rectangle(scramble_image, (i * int(width / 4), int(width / 4)), ((i + 1) * int(width / 4), int(width / 2)),
                      (80, 80, 80), 1)
        if i != 3:
            cv2.rectangle(scramble_image, (int(width / 4), i * int(width / 4)), (int(width / 2), (i + 1) * int(width / 4)),
                          (80, 80, 80), 1)
    return scramble_image


def create_mask(hsv):
    orange_mask = cv2.inRange(hsv, colors.lower_orange, colors.upper_orange)
    green_mask = cv2.inRange(hsv, colors.lower_green, colors.upper_green)
    blue_mask = cv2.inRange(hsv, colors.lower_blue, colors.upper_blue)
    white_mask = cv2.inRange(hsv, colors.lower_white, colors.upper_white)
    red_mask1 = cv2.inRange(hsv, colors.lower_red1, colors.upper_red1)
    red_mask2 = cv2.inRange(hsv, colors.lower_red2, colors.upper_red2)
    red_mask = red_mask1 | red_mask2
    yellow_mask = cv2.inRange(hsv, colors.lower_yellow, colors.upper_yellow)
    mask = orange_mask | green_mask | blue_mask | white_mask | red_mask1 | yellow_mask
    mask_list = (white_mask, red_mask1, green_mask, yellow_mask, orange_mask, blue_mask)
    return mask, mask_list


def fill_scramble_board(board, arr, n):
    height, width, _ = board.shape
    start_pos = (int(width / 4) * position.scramble_board_position[n][0], int(width / 4) *
                 position.scramble_board_position[n][1])

    for i in range(3):
        for j in range(3):
            cv2.rectangle(board, (start_pos[0] + j * int(width / 12), start_pos[1] + i * int(width / 12)),
                          (start_pos[0] + (j + 1) * int(width / 12), start_pos[1] + (i + 1) * int(width / 12)),
                          colors.rgb_colors[arr[i][j]], -1)

    return board


def identify_side_colors(mask_list):
    side = np.zeros((3, 3), dtype=np.uint8)
    for k in range(len(mask_list)):
        for i in range(3):
            for j in range(3):
                frame_part = mask_list[k][i * 80:(i + 1) * 80,
                             j * 80: (j + 1) * 80]
                if (np.count_nonzero(frame_part[10:70, 10:70])) >= 700:
                    # if (np.count_nonzero(frame_part[25:55, 25:55])) >= 350:
                    side[i][j] = k + 1
    return side


def create_n_config_frames(cap, height, width, sides_list):
    font = cv2.FONT_HERSHEY_DUPLEX
    _, frame = cap.read()
    overlay = np.zeros((height, width, 3), np.uint8)
    frame_with_rec = cv2.addWeighted(frame, 0.15, overlay, 0.1, 0)
    x, y = int(width/2), int(height/2)
    cv2.rectangle(frame_with_rec, (x-120, y-120), (x+120, y+120), (0, 0, 255), 5)
    frame_with_rec = cv2.flip(frame_with_rec, 1)
    cv2.putText(frame_with_rec, f'detected sides: {len(sides_list)}', (20, height-20), font, 1,
                (0, 255, 0),
                2, cv2.LINE_4)

    cube_frame = frame[y-120:y+120, x-120:x+120]
    frame_with_rec[y-120:y+120, x-120:x+120] = cv2.flip(cube_frame, 1)
    cv2.GaussianBlur(cube_frame, (5, 5), 0)

    return frame, frame_with_rec, cube_frame


def check_side(frame_with_rec, scramble_image, sides_list, side, width, height, pre_side, counter) -> int:
    x, y = int(width / 2), int(height / 2)
    font = cv2.FONT_HERSHEY_DUPLEX
    if np.count_nonzero(side) == 9:
        cv2.rectangle(frame_with_rec, (x-120, y-120), (x+120, y+120), (0, 255, 255), 5)

        if counter == 50:
            cv2.rectangle(frame_with_rec, (x-120, y-120), (x+120, y+120), (0, 255, 0), 5)
            cv2.waitKey(500)
            is_scanned = True
            for s in sides_list:
                if s[1][1] == side[1][1]:
                    cv2.putText(frame_with_rec, f'scan earlier, move on', (20, 20), font, 1,
                                (0, 0, 255), 2, cv2.LINE_4)
                    is_scanned = False
                    break
            if is_scanned:
                if len(sides_list) == 4:
                    side = np.rot90(side, 1)

                elif len(sides_list) == 5:
                    side = np.rot90(side, -1)

                fill_scramble_board(scramble_image, side, len(sides_list) + 1)
                sides_list.append(side)
                cv2.imshow('scramble', scramble_image)
            if len(sides_list) < 4:
                cv2.putText(frame_with_rec, f'move right side', (x, height - 20), font, 1,
                            (0, 255, 255), 2, cv2.LINE_4)
            elif len(sides_list) == 4:
                cv2.putText(frame_with_rec, f'move up', (x, height - 20), font, 1,
                            (0, 225, 255), 2, cv2.LINE_4)

            elif len(sides_list) == 5:
                cv2.putText(frame_with_rec, f'up twice', (x, height - 20), font, 1,
                            (0, 255, 255), 2, cv2.LINE_4)

            cv2.imshow('frame', frame_with_rec)
            cv2.waitKey(500)

        if np.equal(side, pre_side).all():
            return 1

    return -counter


def recognize_cube(cap):
    sides_list = []
    pre_side = None
    _, frame = cap.read()
    height, width, _ = frame.shape
    scramble_image = create_scramble_board()

    while True:
        counter = 0
        while True:
            frame,  frame_with_rec, cube_frame = create_n_config_frames(cap, height, width, sides_list)
            hsv = cv2.cvtColor(cube_frame, cv2.COLOR_BGR2HSV)
            mask, mask_list = create_mask(hsv)
            result = cv2.bitwise_and(cube_frame, cube_frame, mask=mask)
            side = identify_side_colors(mask_list)
            counter += check_side(frame_with_rec, scramble_image, sides_list, side, width, height, pre_side, counter)

            key = cv2.waitKey(5)

            if key == 27:
                return

            pre_side = side.copy()

            cv2.imshow('result', result)
            cv2.imshow('frame', frame_with_rec)
            cv2.imshow('mask', mask)

            if len(sides_list) == 6:
                return sides_list, scramble_image

            if counter > 50:
                break


def create_scramble(kosiemba_positions, sides_list):
    scramble = ''
    for side in sides_list:
        for j in range(3):
            for k in range(3):
                scramble += kosiemba_positions[side[j][k]]

    return scramble


def destroy_windows():
    windows = ('mask', 'frame', 'result')
    for window in windows:
        cv2.destroyWindow(window)


def show_solution(scramble_image, solution):
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(scramble_image, 'Solution:', (20, scramble_image.shape[0] - 40), font, 0.4,
                (255, 255, 255),
                1, cv2.LINE_4)
    cv2.putText(scramble_image, f'{solution}', (20, scramble_image.shape[0] - 20), font, 0.4,
                (255, 255, 255),
                1, cv2.LINE_4)
    cv2.imshow("scramble", scramble_image)


def main():
    cap = cv2.VideoCapture(0)

    sides_list, scramble_image = recognize_cube(cap)
    cap.release()
    destroy_windows()

    _, sides_list = zip(*sorted(zip(position.sorted_sides, sides_list)))
    kociemba_positions = {sides_list[i - 1][1][1]: colors.kociemba_colors[i] for i in range(1, 7)}
    start_position = position.start_position[(sides_list[0][1][1], sides_list[2][1][1])]

    scramble = create_scramble(kociemba_positions, sides_list)
    solution = find_solution(scramble)
    show_solution(scramble_image, solution)
    threading.Thread(target=create_cube(solution, start_position)).start()


if __name__ == "__main__":
    main()
