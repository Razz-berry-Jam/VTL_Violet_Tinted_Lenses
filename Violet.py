#imports (or lack there off)

def vtl(key, s_message, mode):
    print("Begining verification")

    #characters allowed
    chars = 30

    #fixed wheels disk entry offset and reflector
    disk_entry_offset = 3
    reflector_offset = 3

    #"card reader"
    key_file = open(key, "rt")
    secret_key = key_file.read()
    key_file.close()
    message_file = open(s_message, "rt")
    secret_message = message_file.read()
    message_file.close()

    #the key is a 30*30 grid with no repeat 0 in each column
    #thats 265 million-million-million-million-million different combinations
    error_message = ""
    key_valid = True

    #is the input long enough?
    secret_key = secret_key.replace("\n","")
    s_key_array = []
    if (len(secret_key) != (chars * chars)):
        error_message += "The key is too short, should be 30*30\n"
        key_valid = False

    else:
        count = 0
        col = 0
        row = chars - 1
        cur_row = []
        print("==========================================\n")

        while(count < len(secret_key)):

            if (col == chars):
                col = 0
                row -= 1
                s_key_array.append(cur_row)
                cur_row = []
                print("")

            print(secret_key[count], end="")

            #only using permitted characters
            if (secret_key[count] != '0' and secret_key[count] != '-'):
                error_message += "Incorrect character at location: (" + str(col) + "," + str(row) + ") must be either - or 0\n"
                key_valid = False

            #print("COL:" + str(col) + " ROW: " + str(row))
            cur_row.append(secret_key[count])
            count += 1
            col += 1

        #final row
        s_key_array.append(cur_row)
        print("")
        print("\n==========================================")

        #check that each row and each col only have one 0 in them
        i = 0 
        zero_in_row = 0
        zero_in_col = 0
        while (i < chars):#for each row
            k = 0

            while (k < chars):#for each char in the row
                #check the rows
                if (s_key_array[k][i] == '0'):
                    #print("0 found at (" + str(k) + "," + str(i) + ")")
                    zero_in_row += 1

                #check the cols
                if (s_key_array[i][k] == '0'):
                    #print("0 found at (" + str(i) + "," + str(k) + ")")
                    zero_in_col += 1

                k += 1

            if (zero_in_row != 1):
                error_message += "There must only be one 0 in row: " + str(i) + "\n"
                key_valid = False

            zero_in_row = 0

            if (zero_in_col != 1):
                error_message += "There must only be one 0 in col: " + str(i) + "\n"
                key_valid = False

            zero_in_col = 0
            i += 1

    #check if the message is valid
    translate = ['a','b','c','d','e','f','g','h','i','j',
                 'k','l','m','n','o','p','q','r','s','t',
                 'u','v','w','x','y','z','.',' ','!','?']

    translated_message = []
    message_valid = True
    i = 0

    #for each character of the message:
    #check if it is valid and add it to the translation as a int
    #the int is it's index in translate 
    while (i < len(secret_message)):
        k = 0
        found  = False

        while (k < len(translate)):

            if (secret_message[i] == translate[k]):
                found = True
                translated_message.append(k)

            k += 1

        if (found == False):
            message_valid = False
            error_message += "The character: " + str(secret_message[i]) + " is not a lowercase letter a-z or one of the following 4: [.] [ ] [!] [?]\n"

        i += 1

    if (key_valid == False or message_valid == False):
        print("Error: \n" + error_message)

    else:
        print("The key and message are valid")
        print("Translated message before: " + str(translated_message))

        #these are the ouputs, not A-Z but 30 characters 
        #fialka was in cyrillic so has extra
        #0---0 is the space character traditionaly, the first 30 are letters and ----- is spare
        character_punches  = ['0----','--00-','-00-0','----0','0000-','-0000','000-0','00-0-','-00--','-0---',
                              '00-00','-0-00','-0-0-','000--','00---','--000','--0-0','0-0-0','0--00','-000-',
                              '0-00-','0-0--','---0-','0-000','00--0','--0--','-0--0','00000','---00','0--0-',
                              '-----','0---0'] 

        #substitution matrix for encryption
        matrix_keyboard_to_card = [[1,17],[2,25],[3,30],[4,14],[5,26],[6,21],[7,6],[8,19],[9,1],[10,15],
                                    [11,29],[12,20],[13,4],[14,28],[15,24],[16,2],[17,22],[18,23],[19,18],[20,12],
                                    [21,7],[22,5],[23,27],[24,8],[25,10],[26,9],[27,16],[28,13],[29,11],[30,3]]
        
        #substitution matrix for encryption
        matrix_card_to_disk = [[1,28],[2,14],[3,20],[4,24],[5,2],[6,16],[7,1],[8,10],[9,21],[10,11],
                                    [11,17],[12,13],[13,19],[14,30],[15,5],[16,6],[17,8],[18,15],[19,23],[20,25],
                                    [21,27],[22,18],[23,3],[24,29],[25,26],[26,12],[27,22],[28,7],[29,9],[30,4]]
        
        #wheels using the 3k series wheel configurations
        #they have 30 faces and each face has a pin that can stop the next wheel
        #wheels face above the ruler 0-9 
        wheel_face_index = [0,0,0,0,0,0,0,0,0,0]

        #wheels [wheel_number,face_number,{value, is blocking pin}]
        #1 shows a vlocking pin, 0 is an absence
        wheel_wire_matrix = [[[23,0],[22,1],[3,0],[7,0],[4,1],[8,0],[16,0],[6,0],[10,0],
                   [20,1],[15,1],[17,0],[24,1],[9,0],[30,1],[12,0],[25,1],[11,1],[1,0],
                   [28,0],[27,1],[5,1],[29,0],[26,0],[2,1],[18,0],[21,1],[14,0],[13,1],[19,0]],
                   
                   [[3,0],[24,0],[20,1],[2,0],[6,1],[21,0],[26,1],[7,0],[18,0],
                   [4,0],[17,1],[23,0],[15,1],[19,0],[10,1],[30,1],[13,1],[28,1],[29,1],
                   [11,1],[9,0],[25,1],[1,1],[14,0],[22,1],[8,0],[27,0],[5,1],[12,1],[16,1]],
                   
                   [[20,1],[5,0],[7,0],[15,0],[21,0],[27,0],[4,0],[1,0],[22,1],
                   [17,0],[23,0],[13,0],[30,0],[6,0],[26,0],[10,1],[16,0],[14,1],[19,0],
                   [18,0],[29,0],[24,1],[3,0],[12,0],[9,1],[11,0],[2,0],[28,0],[8,1],[25,0]],
                   
                   [[16,1],[21,0],[28,1],[11,1],[27,1],[3,1],[15,1],[12,0],[24,1],
                   [30,1],[9,0],[17,1],[4,0],[20,1],[25,1],[8,1],[1,1],[29,0],[19,1],
                   [18,1],[14,1],[10,1],[5,1],[23,1],[26,0],[7,1],[6,1],[22,1],[2,0],[13,1]],
                   
                   [[18,0],[15,0],[1,1],[22,0],[19,1],[16,0],[29,1],[8,1],[17,0],
                   [4,0],[3,0],[14,0],[6,0],[30,1],[23,0],[5,0],[26,1],[13,1],[25,0],
                   [10,0],[12,0],[21,0],[27,1],[20,0],[7,0],[11,0],[24,0],[9,0],[2,0],[28,0]],
                   
                   [[9,0],[14,0],[13,0],[20,1],[24,0],[8,0],[2,0],[6,0],[5,1],
                   [19,0],[11,0],[28,1],[30,0],[3,0],[18,0],[15,0],[7,1],[25,1],[16,1],
                   [1,1],[12,0],[23,0],[27,1],[29,0],[17,1],[10,1],[21,1],[4,1],[22,0],[26,1]],
                   
                   [[7,1],[9,0],[5,1],[26,1],[6,1],[4,1],[19,1],[3,1],[8,0],
                   [28,1],[22,1],[12,1],[21,1],[24,1],[23,1],[10,0],[13,0],[1,1],[16,0],
                   [29,1],[2,1],[25,1],[27,1],[15,0],[18,1],[11,1],[14,1],[17,1],[30,0],[20,1]],
                   
                   [[29,0],[27,0],[15,0],[13,1],[8,0],[2,0],[25,0],[12,0],[6,0],
                   [23,0],[9,1],[18,1],[24,1],[1,0],[14,0],[21,0],[17,0],[10,0],[3,0],
                   [11,0],[22,0],[7,1],[16,0],[4,0],[19,1],[26,0],[5,0],[30,0],[28,0],[20,1]],
                   
                   [[5,1],[19,1],[2,1],[27,1],[20,0],[26,1],[7,0],[11,1],[16,0],
                   [18,0],[3,1],[13,1],[4,0],[23,1],[28,0],[21,1],[6,0],[24,0],[29,0],
                   [30,0],[15,1],[17,1],[9,1],[12,1],[8,1],[22,1],[25,0],[10,0],[1,1],[14,0]],
                   
                   [[20,0],[24,0],[8,0],[25,0],[19,1],[1,0],[17,0],[5,1],[15,0],
                   [27,0],[9,1],[12,0],[22,1],[10,1],[18,1],[3,0],[16,0],[30,0],[4,0],
                   [14,1],[7,1],[23,0],[11,0],[2,1],[29,1],[26,0],[28,1],[21,1],[6,1],[13,0]]]
        
        #reflector matrix with endode and decode modes encode:[0,X] decode:[1,X]
        reflector_matrix = [[23,6,20,28,14,2,12,17,22,11,10,7,13,5,29,18,8,24,27,3,25,9,1,16,21,30,19,4,15,26],
                            [23,6,20,28,14,2,12,17,22,11,10,7,13,5,29,24,8,16,27,3,25,9,1,18,21,30,19,4,15,26],
                            [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]]

        finished_encoding = 0

        #while we have not encoded all letters of the message
        #need to encode one at a time as the wheels step
        while (finished_encoding < (len(translated_message))): 
            cur_char = translated_message[finished_encoding]
              
            #convert key top / input letter to cyrillic letter
            #cyrillic letters can be treated as numbers 0-29, the index of the above
            #translated_message is an array containing the translation
            #output valid

            #substitution for keyboard to card reader
            cur_char = matrix_keyboard_to_card[cur_char][1] -1
            #output valid

            #substitution by card reader (using s_key_array)
            k = 0
            while (k < chars):#for each character in the grid
                #we know the row find the column
                if (s_key_array[k][cur_char] == '0'):
                    cur_char = k
                    k= chars + 1
                k += 1
            #output valid
            
            #substitution from card reader to entry disk
            cur_char = matrix_card_to_disk[cur_char][1] -1 
            #output valid

            # +3
            cur_char = (cur_char + disk_entry_offset) % chars
            #output valid


            #subsitution for each of the rotors from 10 to 1:
            cur_wheel = 9
            while (cur_wheel > -1):
                #add current position of the wheel (the letter that would be visable above the ruler)
                cur_char += wheel_face_index[cur_wheel] #value is not 0 index
                cur_char = cur_char % chars
                #outputs a number 0-29

                #substitution by wheel wiring matrix
                cur_char = wheel_wire_matrix[cur_wheel][cur_char][0] -1
                #output a number 0-29

                #subtract current position of the wheel
                cur_char -= wheel_face_index[cur_wheel]
                cur_char = cur_char % chars
                #output a number 0-29

                cur_wheel -= 1
            
            # -3
            cur_char = (cur_char - disk_entry_offset) % chars
            cur_char = (cur_char + reflector_offset) % chars
            #output valid

            #substitution by the reflector
            #different reflector for encoding and decoding 
            #mode 0 = encode, 1 = decode, 2 = plaintext
            cur_char = reflector_matrix[mode][cur_char] -1
            #output valid

            # +3
            cur_char = (cur_char - reflector_offset) % chars
            cur_char = (cur_char + disk_entry_offset) % chars
            #output valid

            #inverse substitution for each of the rotors 1 to 10:
            cur_wheel = 0

            while (cur_wheel < 10):
                #add current position of the wheel (the letter that would be visable above the ruler)
                cur_char += wheel_face_index[cur_wheel] #value is not 0 index
                cur_char = cur_char % chars
                #outputs a number 0-29

                #tar = cur_char + 1

                #inverse substitution by wheel wiring matrix
                k = 0
                while (k < chars):
                    #cur_spot = wheel_wire_matrix[cur_wheel][k][0]
                    if (wheel_wire_matrix[cur_wheel][k][0] == cur_char + 1):
                        cur_char = k
                        k = chars + 1
                    k += 1
                cur_char = cur_char % chars
                #output a number 0-29

                #subtract current position of the wheel
                cur_char -= wheel_face_index[cur_wheel]
                cur_char = cur_char % chars
                #output a number 0-29

                cur_wheel += 1

            # -3
            cur_char = (cur_char - disk_entry_offset) % chars
            #output valid

            #inverse substitution for entry disk to card reader
            k = 0
            while (k < chars):
                if (matrix_card_to_disk[k][1] == cur_char + 1):
                    cur_char = matrix_card_to_disk[k][0] - 1
                    k= chars + 1
                k += 1
            #output valid

            #inverse substitution by card reader 
            k = 0
            while (k < chars):#for each character in the grid
                #we know the column find the row
                if (s_key_array[cur_char][k] == '0'):
                    cur_char = k
                    k= chars + 1
                k += 1
            #output valid

            #inverse substitution from card reader to keyboard
            k = 0
            while (k < chars):
                if (matrix_keyboard_to_card[k][1] == cur_char + 1):
                    cur_char = matrix_keyboard_to_card[k][0] - 1
                    k= chars + 1
                k += 1
            #output valid

            #punch the letter
            translated_message[finished_encoding] = cur_char

            #step
            #9-7-5-3-1 anticlockwise rotation, letters get bigger b->c
            done_steping = False
            cur_wheel = 8 #0 index

            while (done_steping == False):
                #step this wheel
                wheel_face_index[cur_wheel] += 1
                wheel_face_index[cur_wheel] = wheel_face_index[cur_wheel] % chars
                #keep it 0-29

                #do we step the next?
                if ((cur_wheel - 2 < 0) or (wheel_wire_matrix[cur_wheel][wheel_face_index[cur_wheel]][1] == 1)): #0 = no blocking pin, 1 = blocking pin
                    done_steping = True
                
                cur_wheel -= 2

            #2-4-6-8-10 clockwise rotation, letters get smaller b->a
            done_steping = False
            cur_wheel = 1 #0 index

            while (done_steping == False):
                #step this wheel
                wheel_face_index[cur_wheel] += 1
                wheel_face_index[cur_wheel] = wheel_face_index[cur_wheel] % chars
                #keep it 0-29

                #do we step the next?
                if ((cur_wheel + 2 > 9) or (wheel_wire_matrix[cur_wheel][wheel_face_index[cur_wheel]][1] == 1)): #0 = no blocking pin, 1 = blocking pin
                    done_steping = True

                cur_wheel += 2

            #do the next letter
            finished_encoding += 1

            #testing
            #finished_encoding = 999999

        print("Translated message after: " + str(translated_message))
        #output in plain text
        output = ""
        count  = 0

        while (count < len(translated_message)):
            output += translate[translated_message[count]]
            count += 1

        print(output)