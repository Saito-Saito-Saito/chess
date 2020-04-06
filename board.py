#! /usr/bin/env python3
# board.py

import re
import copy

from config import *
import fundam
import IO


class Board:    
    def __init__(self, input_board=[], input_taget=[], input_k=[], input_q=[]):
        if len(input_board) == 8:
            self.board = copy.deepcopy(input_board)
        else:
            self.board = [
                [R, P, 0, 0, 0, 0, -P, -R],
                [N, P, 0, 0, 0, 0, -P, -N],
                [B, P, 0, 0, 0, 0, -P, -B],
                [Q, P, 0, 0, 0, 0, -P, -Q],
                [K, P, 0, 0, 0, 0, -P, -K],
                [B, P, 0, 0, 0, 0, -P, -B],
                [N, P, 0, 0, 0, 0, -P, -N],
                [R, P, 0, 0, 0, 0, -P, -R]
            ]
        self.ep_target = [OVERSIZE, OVERSIZE]
        self.castl_k = [WHITE, BLACK]
        self.castl_q = [WHITE, BLACK]


    def BOARDprint(self):
        print('\n')
        print('\t    a   b   c   d   e   f   g   h')
        print('\t   -------------------------------')
        for row in range(SIZE - 1, -1, -1):
            print('\t{} |'.format(row + 1), end='')
            for col in range(SIZE):
                print(' {} |'.format(IO.ToggleType(self.board[col][row])), end='')
            print(' {}'.format(row + 1))
            print('\t   -------------------------------')
        print('\t    a   b   c   d   e   f   g   h')
        print('\n')
    

    def motionjudge(self, frCOL, frROW, toCOL, toROW, promote=EMPTY):
        # inside / out of the board
        if not (fundam.InSize(frCOL) and fundam.InSize(frROW) and fundam.InSize(toCOL) and fundam.InSize(toROW)):
            logging.debug('OUT OF THE BOARD')
            return False

        player = fundam.PosNeg(self.board[frCOL][frROW])
        piece = abs(self.board[frCOL][frROW])
        
        # moving to the square where there is  own piece
        if fundam.PosNeg(self.board[toCOL][toROW]) == player:
            logging.debug('MOVING TO OWN SQUARE')
            return False

        # there is no piece at Fr
        if piece == EMPTY:
            logging.debug('MOVING EMPTY')
            return False

        # PAWN
        elif piece == PAWN:
            # not promoting at the edge
            if (toROW == 8 - 1 or toROW == 1 - 1) and promote not in [R, N, B, Q]:
                logging.debug('NECESSARY TO PROMOTE')
                return False
            # normal motion (one step forward); the same COL, appropriate ROW, TO = EMPTY
            # note: if player is WHITE (=1), the row number has to increase
            if frCOL == toCOL and toROW - frROW == player and self.board[toCOL][toROW] == EMPTY:
                return True
            # normal capturing; next COL, appropriate ROW, TO = opponent
            if abs(toCOL - frCOL) == 1 and toROW - frROW == player and fundam.PosNeg(self.board[toCOL][toROW]) == -player:
                return True
            # first two steps; adequate frROW the same COL, appropriate ROW, passing squares are EMPTY
            if ((player == WHITE and frROW == 2 - 1) or (player == BLACK and frROW == 7 - 1)) and frCOL == toCOL and toROW - frROW == 2 * player and self.board[frCOL][frROW + player] == self.board[toCOL][toROW] == EMPTY:
                return True
            # en passant; FR - ep_target, TO - ep_target, TO = EMPTY
            if abs(self.ep_target[COL] - frCOL) == 1 and frROW == self.ep_target[ROW] and toCOL == self.ep_target[COL] and toROW - self.ep_target[ROW] == player and self.board[toCOL][toROW] == EMPTY:
                return True
            # all other moves are invalid
            logging.debug('INVALID MOTION of PAWN')
            return False

        # ROOK
        elif piece == ROOK:
            # invalid motion
            if frCOL != toCOL and frROW != toROW:
                logging.debug('INVALID MOTION of ROOK')
                return False
            # else, necessary to check whether there is an obstacle in the way

        # KNIGHT
        elif piece == KNIGHT:
            # valid motion
            if (abs(toCOL - frCOL) == 1 and abs(toROW - frROW) == 2) or (abs(toCOL - frCOL) == 2 and abs(toROW - frROW) == 1):
                return True
            # all other motion is invalid
            logging.debug('INVALID MOTION of KNIGHT')
            return False

        # BISHOP
        elif piece == BISHOP:
            # invalid motion
            if abs(toCOL - frCOL) != abs(toROW - frROW):
                logging.debug('INVALID MOTION of BISHOP')
                return False
            # else, necessary to check an obstacle in the way

        # QUEEN
        elif piece == QUEEN:
            # invalid motion (cf, B/R)
            if frCOL != toCOL and frROW != toROW and abs(toCOL - frCOL) != abs(toROW - frROW):
                logging.debug('INVALID MOTION of QUEEN')
                return False
            # else, necessary to check an obstacle in the way

        # KING
        elif piece == KING:
            # normal motion (one step)
            if abs(toCOL - frCOL) <= 1 and abs(toROW - frROW) <= 1:
                logging.info('KING NORMAL')
                return True
            # castling
            if player == WHITE:
                row = 1 - 1
            elif player == BLACK:
                row = 8 - 1
            else:
                logging.error('UNEXPECTED PLAYER VALUE in motionjudge')
                return False
            # Q-side
            if player in self.castl_q and frCOL == e - 1 and frROW == row and toCOL == c - 1 and toROW == row and self.board[b - 1][row] == self.board[c - 1][row] == self.board[d - 1][row] == EMPTY:
                logging.debug('KING Q-side')
                return True
            # K-side
            if player in self.castl_k and frCOL == e - 1 and frROW == row and toCOL == g - 1 and toROW == row and self.board[f - 1][row] == self.board[g - 1][row] == EMPTY:
                logging.debug('KING K-side')
                return True
            # all other moves are invalid
            logging.debug('INVALID MOTION of KING')
            return False

        # other piece values
        else:
            logging.error('UNEXPECTED VALUE of PIECE in motionjudge')
            return False

        # whether there is an obstacle in the wauy of R/B/Q
        direction = [fundam.PosNeg(toCOL - frCOL), fundam.PosNeg(toROW - frROW)]
        focused = [frCOL + direction[COL], frROW + direction[ROW]]
        while focused[COL] != toCOL or focused[ROW] != toROW:
            if not (fundam.InSize(focused[0]) and fundam.InSize(focused[1])):
                break
            if self.board[focused[COL]][focused[ROW]] != EMPTY:
                logging.info('THERE IS AN OBSTACLE in the way')
                return False
            focused[COL] += direction[COL]
            focused[ROW] += direction[ROW]
        # there is nothing in the wauy
        return True

    
    def move(self, frCOL, frROW, toCOL, toROW, promote=EMPTY):
        # invalid motion
        if self.motionjudge(frCOL, frROW, toCOL, toROW, promote) == False:
            return False
        
        piece = abs(self.board[frCOL][frROW])
        player = fundam.PosNeg(self.board[frCOL][frROW])

        # castling
        if piece == KING and abs(toCOL - frCOL) > 1:
            if player == WHITE:
                row = 1 - 1
            elif player == BLACK:
                row = 8 - 1
            else:
                logging.error('UNEXPECTED VALUE of PLAYER in move')
                return False
            # moving rook
            if toCOL == c - 1:
                self.board[d - 1][row] = player * ROOK
                self.board[a - 1][row] = EMPTY
            elif toCOL == g - 1:
                self.board[f - 1][row] = player * ROOK
                self.board[h - 1][row] = EMPTY
            else:
                logging.error('UNEXPECTED VALUE of toCOL in move')
                return False

        # en passant
        if piece == PAWN and frCOL != toCOL and self.board[toCOL][toROW] == EMPTY:
            # capturing opponent's pawn
            self.board[toCOL][frROW] = EMPTY
        
        # promotion
        if piece == PAWN and (toROW == 8 - 1 or toROW == 1 - 1):
            self.board[frCOL][frROW] = player * promote
        
        # moving own piece
        self.board[toCOL][toROW] = self.board[frCOL][frROW]
        self.board[frCOL][frROW] = EMPTY
        # return as succeeded
        return True


    def king_place(self, player):
        # searching for the checkee's king
        for col in range(SIZE):
            if player * KING in self.board[col]:
                return [col, self.board[col].index(player * KING)]
        else:
            # there is no king
            return EMPTY
            

    def checkcounter(self, checkee):
        #if there is no king, impossible to check
        TO = self.king_place(checkee)
        try:
            toCOL = TO[COL]
            toROW = TO[ROW]
        except:
            logging.debug('THERE IS NO KING')
            return False

        # count up the checking pieces
        count = 0
        for frCOL in range(SIZE):
            for frROW in range(SIZE):
                if fundam.PosNeg(self.board[frCOL][frROW]) == -checkee and self.motionjudge(frCOL, frROW, toCOL, toROW, Q):
                    logging.warning('CHECK: {}, {} -> {}, {}'.format(frCOL, frROW, toCOL, toROW))
                    count += 1
        # if checkee is not checked, return 0
        return count


    def checkmatejudge(self, matee):
        # if not checked, it's not checkmate
        if self.checkcounter(matee) in [False, 0]:
            return False
        
        # searching for all the moves matee can
        for frCOL in range(SIZE):
            for frROW in range(SIZE):
                if fundam.PosNeg(self.board[frCOL][frROW]) == matee:
                    for toCOL in range(SIZE):
                        for toROW in range(SIZE):
                            # cloning board
                            local_board = Board(self.board, self.ep_target, self.castl_k, self.castl_q)
                            if local_board.move(frCOL, frROW, toCOL, toROW, Q) and local_board.checkcounter(matee) == 0:
                                logging.info('THERE IS {}, {} -> {}, {}'.format(frCOL,frROW,toCOL,toROW))
                                return False
                    logging.info('"FR = {}, {}" was unavailable'.format(frCOL, frROW))

        # completing the loop, there is no way to flee
        return True

    
    def stalematejudge(self, matee):
        # if checked, it's not stalemate
        if self.checkcounter(matee) not in [0, False]:
            logging.debug('CHECKED')
            return False

        # searching all the moves for one that can move without being checked
        for frCOL in range(SIZE):
            for frROW in range(SIZE):
                if fundam.PosNeg(self.board[frCOL][frROW]) == matee:
                    for toCOL in range(SIZE):
                        for toROW in range(SIZE):
                            local_board = Board(self.board, self.ep_target, self.castl_k, self.castl_q)
                            # in case it is not checked after moving
                            motion = local_board.move(frCOL, frROW, toCOL, toROW, Q)
                            count = local_board.checkcounter(matee)
                            logging.debug('motion: {}, count: {}'.format(motion, count))
                            if motion and count in [0, False]:
                                logging.info('THERE IS {}, {} -> {}, {}'.format(frCOL, frROW, toCOL, toROW))
                                return False
        # completing the loop, there is no way to avoid check when moving
        return True
    

    def s_analyze(self, s, player):
        # avoiding bugs
        if len(s) == 0:
            logging.debug('len(s) == 0')
            return False

        # deleting all of !?+-= at the tail
        while s[-1] in ['!', '?']:
            s = s.rstrip(s[-1])

        # avoiding bugs
        if len(s) == 0:
            logging.debug('len(s) == 0')
            return False

        # matching the normal format
        match = re.match(r'^[PRNBQK]?[a-h]?[1-8]?[x]?[a-h][1-8](=[RNBQ]|e.p.)?[\+#]?$', s)

        if match:
            line = match.group()
            logging.info('line = {}'.format(line))

            # what piece is moving
            if line[0] in ['R', 'N', 'B', 'Q', 'K']:
                piece = IO.ToggleType(line[0])
                line = line.lstrip(line[0])
            else:
                piece = PAWN
            logging.info('PIECE == {}'.format(piece))

            # written info of what row the piece comes from
            if line[0].isdecimal():
                frCOL = OVERSIZE
                frROW = IO.ToggleType(line[0]) - 1
                line = line.lstrip(line[0])
            # written info of what col the piecce comes from
            elif ord('a') <= ord(line[0]) <= ord('h') and ord('a') <= ord(line[1]) <= ord('x'):
                frCOL = IO.ToggleType(line[0]) - 1
                frROW = OVERSIZE
                line = line.lstrip(line[0])
            # nothing is written about where the piece comes from
            else:
                frCOL = OVERSIZE
                frROW = OVERSIZE
            logging.info('FR = {}, {}'.format(frCOL, frROW))

            # whether the piece has captured one of the opponent's pieces
            if line[0] == 'x':
                CAPTURED = True
                line = line.lstrip(line[0])
            else:
                CAPTURED = False

            # where the piece goes to
            toCOL = IO.ToggleType(line[0]) - 1
            toROW = IO.ToggleType(line[1]) - 1
            logging.info('TO = {}, {}'.format(toCOL, toROW))

            # promotion
            if '=' in line:
                promote = line[line.index('=') + 1]
            else:
                promote = EMPTY

            # raising up all the available candidates
            candidates = []
            for col in range(SIZE):
                # when frCOL is written
                if fundam.InSize(frCOL) and frCOL != col:
                    continue

                for row in range(SIZE):
                    # when frROW is written
                    if fundam.InSize(frROW) and frROW != row:
                        continue

                    # piece
                    if self.board[col][row] != player * piece:
                        continue

                    # available motion
                    if self.motionjudge(col, row, toCOL, toROW, promote) == False:
                        continue

                    candidates.append([col, row])
            logging.info('candidates = {}'.format(candidates))

            # checking all the candidates
            for reference in range(len(candidates)):
                local_board = Board(self.board, self.ep_target, self.castl_k, self.castl_q)
                local_board.move(candidates[reference][COL], candidates[reference][ROW], toCOL, toROW, promote)

                # capture; searching for the opponent's piece that has disappeared
                if CAPTURED or 'e.p.' in line:
                    for col in range(SIZE):
                        for row in range(SIZE):
                            if fundam.PosNeg(self.board[col][row]) == -player and fundam.PosNeg(local_board.board[col][row]) != -player:
                                break
                        else:
                            continue
                        break
                    else:
                        # it does not capture any piece
                        logging.info('{} does not capture cany piece'.format(candidates[reference]))
                        del candidates[reference]
                        reference -= 1
                        continue

                # check
                if line.count('+') > local_board.checkcounter(-player):
                    logging.info('{} is short of the number of check'.format(candidates[reference]))
                    del candidates[reference]
                    reference -= 1
                    continue

                # checkmate
                if '#' in line and local_board.checkmatejudge(-player) == False:
                    logging.info('{} does not checkmate'.format(candidates[reference]))
                    del candidates[reference]
                    reference -= 1
                    continue

                # en passant
                if 'e.p.' in line and self.board[toCOL][toROW] != EMPTY:
                    logging.info('{} does not en passant'.format(candidates[reference]))
                    del candidates[reference]
                    reference -= 1
                    continue

            # return
            if len(candidates) == 1:
                logging.info('NORMALLY RETURNED from s_analyze')
                return [candidates[0][COL], candidates[0][ROW], toCOL, toROW, promote]
            elif len(candidates) > 1:
                logging.warning('THERE IS ANOTHER MOVE')
                return [candidates[0][COL], candidates[0][ROW], toCOL, toROW, promote]
            else:
                logging.info('THERE IS NO MOVE')
                return False

        # in case the format does not match
        else:
            # check whether it represents castling
            if player == WHITE:
                row = 1 - 1
            elif player == BLACK:
                row = 8 - 1
            else:
                logging.error('UNEXPECTED PLAYER VALUE in s_analyze')
                return False

            # Q-side
            if s in ['O-O-O', 'o-o-o', '0-0-0'] and self.board[e - 1][row] == player * KING:
                logging.info('format is {}, castl is {}'.format(s, self.castl_q))
                return [e - 1, row, c - 1, row, EMPTY]
            # K-side
            elif s in ['O-O', 'o-o', '0-0'] and self.board[e - 1][row] == player * KING:
                logging.info('format is {}, castl is {}'.format(s, self.castl_k))
                return [e - 1, row, g - 1, row, EMPTY]
            else:
                logging.debug('INVALID FORMAT')
                return False
