import binascii

var = -1

def hex_char_to_int(hex_char):
    match hex_char:
        case 'a':
            return 10
        case 'b':
            return 11
        case 'c':
            return 12
        case 'd':
            return 13
        case 'e':
            return 14
        case 'f':
            return 15
        case _:
            return int(hex_char) #wild card
        
def hexToASCII(hexx):
    ascii = ""
    for i in range(0, len(hexx), 2):
        # extract two characters from hex string
        part = hexx[i : i + 2]

        # change it into base 16 and
        # typecast as the character 
        ch = chr(int(part, 16))

        # add this char to final ASCII string
        ascii += ch

    return ascii

def box_size(hex_bits):#this just convers a section of hex into an int
    size = 0
    #0 index it
    count = len(hex_bits) - 1 

    for i in hex_bits:
        val =  hex_char_to_int(i)
        size += (val * (pow(16, count)))
        count -= 1

    return size

def box_digging(hex_data, 
                start, 
                end, 
                target_list, 
                cur_target):#recursive search down box structure
    target = target_list[cur_target]
    print ("\n-------------------")
    print ("Finding target: " + target)

    cur_index = start + 16

    #test
    #stsd specificaly has a ver and flags so we need to skip 24 not 16
    #so if our target is stsd we increse the passed index by 4 before continuing
    if (target == "avc1"):
        cur_index += 16#hard coding the additional offset
    #test

    tar_index = -1
    while cur_index < end:
        #get the size and name
        size = box_size(hex_data[cur_index:cur_index + 8]) 
        name = hexToASCII(hex_data[cur_index + 8:cur_index + 16])

        #do stuff
        print("Name: " + str(name) + " Size: " + str(size))

        #did we find the last target?
        if cur_target+1 >= len(target_list):
            #done
            tar_index = cur_index

        elif (name == target):
            #keep digging
            box_digging(hex_data, 
                        cur_index, 
                        (cur_index + size * 2), 
                        target_list, 
                        cur_target + 1)

        #in hex, go to the next box
        cur_index += size * 2 

    if (tar_index != -1):
        print("Target found")
        global var
        var = tar_index
    print ("-------------------\n")

#we hit the target now find everything inside it
def box_harvest(hex_data, start):
    end = start // 2 + box_size(hex_data[start:start+8])
    host = hexToASCII(hex_data[start + 8:start + 16])
    print ("\n+++++++++++++++++++")
    print ("Harvesting boxes from: " + str(host))
    cur_index = start + 16
    boxes = []

    while cur_index < end * 2:
        #in bytes
        size = box_size(hex_data[cur_index:cur_index +8])
        name = hexToASCII(hex_data[cur_index + 8:cur_index + 16])

        print("Name: " + str(name) + " Size: " + str(size))
        boxes.append([name,str(cur_index // 2),str(size)])
        cur_index += size * 2 #in hex, go to the next box

    print ("+++++++++++++++++++\n")
    return boxes

def read_file(vid_path):
    print("read boxes for video at path: " + str(vid_path))
    with open(str(vid_path), "rb") as vid:#as binary
    
        hex_data = binascii.hexlify(vid.read())

        #the ' marks the start of the encoded bytes
        start = str(hex_data).find("'") + 1 

        #it also marks the end of the encoded bytes
        end = str(hex_data).find("'", start) 

        encoded_hex_data  = str(hex_data)[start:end]
        
        #the end goal, boxes that house the data we need to identify frame data

        root_targets = ["trak","mdia","minf","stbl"]
        s_targets = ["stss", "stts","stsc","stsz","stco"]
        s_boxes = []

        #boxes
        end_index = len(encoded_hex_data)
        cur_index = 0
        global var
        while cur_index < end_index:
            size = box_size(encoded_hex_data[cur_index:cur_index+8]) #in bytes
            name = hexToASCII(encoded_hex_data[cur_index+8:cur_index+16])

            print("Name: " + str(name) + " Size: " + str(size))

            #finding moov, the host box
            #did we find it?
            if name=="moov": 
                #look for stbl, the end goal for this section
                box_digging(encoded_hex_data, cur_index, (cur_index + size * 2), root_targets, 0)

                if (var == -1):
                    print("Error: Could not find stbl")

                else:
                    print("Index of stbl: " + str(var))
                    #find moov, trak, mdia, minf, stbl
                    s_boxes = box_harvest(encoded_hex_data, var)
                    #print (boxes)

            cur_index += size*2 #in hex, go to the next box

        #inside stable we want: stss, stts, stsc, stsz, stco/co64
        #check locations are correct
        count = 0
        target_boxes = [{"","",""},{"","",""},{"","",""},{"","",""},{"","",""}]

        for i in range (len(s_boxes)):
            for j in range (len(s_targets)):
                if s_boxes[i][0] ==  s_targets[j]:
                    count += 1
                    target_boxes[j] = s_boxes[i] #in the same order as the list

        if count == 5:
            print("Found all five required boxes")
            #name, index, size
            #we have the required boxes analyse them one at a time

            #stco
            #4 bytes size, 4b type/name, 4b version and flags
            #4 of entries and then the chunk offset table
            index=int(target_boxes[4][1]) * 2 
            size=int(target_boxes[4][2]) * 2
            name = hexToASCII(encoded_hex_data[index + 8:index + 16])
            no_chunks = box_size(encoded_hex_data[index + 24:index + 32])
            print(name + " number of chunks: " + str(no_chunks))

            #generate chunk table
            #read everything from index+32 until the end of the doc, index+size
            chunk_table_raw = encoded_hex_data[index + 32:index + size]
            table_entry_size = (len(chunk_table_raw) // no_chunks)
            count = 0
            cur_index = index + 32
            chunk_table_data = [-1] * no_chunks

            while count < no_chunks:
                chunk_table_data[count] = box_size(encoded_hex_data[cur_index:cur_index + table_entry_size])
                #print("Chunk: " + str(count) + " = " + str(chunk_table_data[count]))
                count += 1
                cur_index += table_entry_size

            #we now have all the offsets for chunks where samples/frames are stored in mdat 
            #this works because whilst the chunks are not evenly sized the amount of data used to store there size is
            #this means you can loop through the storage for the data
            #split into even segments and accuratly get the offset of each one
            
            #stsz
            #we can grab the: sample count - number of frames, sample size - the size of each sample
            index=int(target_boxes[3][1]) * 2 #hex->bytes tarnaslation
            size=int(target_boxes[3][2]) * 2
            name = hexToASCII(encoded_hex_data[index + 8:index + 16])
            sample_size = box_size(encoded_hex_data[index + 24:index + 32])
            sample_count = box_size(encoded_hex_data[index + 32:index + 40])

            sample_size_table = [-1] * sample_count
            sample_size_raw = encoded_hex_data[index + 40:index + size]
            table_entry_size = (len(sample_size_raw) // sample_count)
            count = 0
            cur_index = index + 40

            if (sample_size == 0):
                #not uniform in size
                print("Not uniform sample size identified, one moment please")

                while count < sample_count:
                    sample_size_table[count] = box_size(encoded_hex_data[cur_index:cur_index + table_entry_size])
                    #print("Sample: " + str(count) + " = " + str(sample_size_table[count]))
                    count += 1
                    cur_index += table_entry_size

            #now we have the number of samples and the size of each sample
            print(name + " number of samples: " + str(sample_count))

            #stsc
            #the sample to chunk data, a table that contains chunk location data
            #chunks can be consecutive, so if we have two records here that means:
            #chunks a-f are all together and chunks g-k are all together
            #the sample descritpion id relates to stsd
            index=int(target_boxes[2][1]) * 2 #hex->bytes tarnaslation
            size=int(target_boxes[2][2]) * 2
            name = hexToASCII(encoded_hex_data[index + 8:index + 16])
            no_entries = box_size(encoded_hex_data[index + 24:index + 32])

            #read each entry out into an array
            sample_chunk_table = [{999,999,999}] * no_entries
            count = 0
            cur_index = index + 32

            while count < no_entries:
                #the table is 4bytes a peice: first chunk, samples in chunk, sample description
                first_chunk = box_size(encoded_hex_data[cur_index:cur_index + 8])
                samples_per_chunk = box_size(encoded_hex_data[cur_index + 8:cur_index + 16])
                sample_description = box_size(encoded_hex_data[cur_index + 16:cur_index + 24])
                #print ("FC: " + str(first_chunk) + " SPC: " + str(samples_per_chunk) + " SD: " + str(sample_description))
                entry = [first_chunk, samples_per_chunk, sample_description]
                sample_chunk_table[count] = entry
                count += 1
                cur_index += 24

            print(name + " number of seperated groups of chunks: " + str(no_entries))
            #print(sample_chunk_table)
            #okay so sample chunk table is a 2d arry with [x][y][z]
            #x is each group of chunks
            #y is the number of samples in each chunk
            #z is the corresponding stsd description

            #okay running a test, what about one sample?
            #samples can be of a size thats an odd number of bytes, so we need to work in bytes not hex for this
            
            #1) read the file as bytes
            vid.seek(0) #go back to the start of the file
            raw_byte_data = vid.read()
            #2) go to each sample offset and read using the size in bytes
            #they need to be decoded in order idealy

            #stts contains the decoding oder for the samples
            index=int(target_boxes[1][1]) * 2 #hex->bytes tarnaslation
            size=int(target_boxes[1][2]) * 2
            name = hexToASCII(encoded_hex_data[index+8:index+16])
            no_entries = box_size(encoded_hex_data[index+24:index+32])
            print(name + " number of entries: " + str(no_entries))

            if (no_entries != 1):
                print("Data is sotred in a non sequential order, the version is incompatable with this data")

            else:
                #ctts can contain the display order if it is not decoding order
                #stss identifies keyframes
                index=int(target_boxes[0][1]) * 2 #hex->bytes tarnaslation
                size=int(target_boxes[0][2]) * 2
                name = hexToASCII(encoded_hex_data[index+8:index+16])
                no_key_frames = box_size(encoded_hex_data[index+24:index+32])
                print(name + " number of keyframes: " + str(no_key_frames))
                count = 0
                cur_index = index + 32
                key_frames = [-1] * no_key_frames

                while count < no_key_frames:
                    key_frames[count] = box_size(encoded_hex_data[cur_index:cur_index+8])
                    cur_index += 8
                    count += 1
                
                #3) store them in an array
                #so the samples are stored in the same order they are output
                #for each group of chunks
                samples = [-1] * sample_count

                no_groups = len(sample_chunk_table)
                cur_group = 0
                cur_chunk = 0
                cur_sample = 0

                while (cur_group < no_groups):
                    print("Reading group #" + str(cur_group + 1))
                    #is this the last group?
                    no_chunks_in_group = -1
                    no_samples_in_chunk = sample_chunk_table[cur_group][1]

                    if ((cur_group + 1) == no_groups):
                        #this is the last
                        #e.g. if we have 30 chunks and the first is the 20th
                        #then the no in this group is 21 [20, 21, 22... 30]
                        no_chunks_in_group = no_chunks - sample_chunk_table[cur_group][0] + 1

                    else:
                        #this is not the last
                        #e.g. if the first here is 10th and the next groups first is the 20th
                        #then the no in this group is 10 [10, 11, 12... 19]
                        no_chunks_in_group = sample_chunk_table[cur_group + 1][0] - sample_chunk_table[cur_group][0]

                    print("Number of chunks in this group = " + str(no_chunks_in_group))
                    
                    #for each chunk in that group
                    cur_chunk_in_group = 0
                    while (cur_chunk_in_group < no_chunks_in_group):
                        print("Reading chunk #" + str(cur_chunk + 1))

                        cur_chunk_index = chunk_table_data[cur_chunk]
                        cur_sample_offset = 0

                        #for each sample in that chunk
                        cur_sample_in_chunk = 0
                        print("Reading samples", end="")

                        while (cur_sample_in_chunk < no_samples_in_chunk):
                            print(".", end="")
                            #get get the size of the sample
                            cur_sample_size = sample_size #uniform size

                            if (sample_size == 0): #not uniform size
                                cur_sample_size = sample_size_table[cur_sample]

                            cur_sample_index = cur_chunk_index + cur_sample_offset
                            #read the data into an array
                            #the locations are in bytes, not hex
                            #we need to use the raw byte data raw_byte_data
                            #starting at the index gievn and stopping at the end of the size
                            samples[cur_sample] = raw_byte_data[cur_sample_index:cur_sample_index+cur_sample_size]

                            cur_sample_offset += cur_sample_size
                            cur_sample += 1
                            cur_sample_in_chunk += 1

                        print("")#for the display
                        cur_chunk += 1
                        cur_chunk_in_group += 1

                    cur_group +=1
 
                #4) MP4 -> annexB
                #okay so we will assume for the now the format is only H.264
                #dont worry the test file cat.mp4 is avcC H.264

                #we need the avcc box for SPS and PP

                #get our start
                stbl_index = var 

                #reset the return
                var = -1
                size = box_size(encoded_hex_data[stbl_index:stbl_index+8]) #in bytes
                new_targets = ["stsd","avc1"]
                box_digging(encoded_hex_data, stbl_index, (stbl_index + size*2), new_targets, 0)

                #find avcC
                cur_index = var
                avcc_index = -1
                var = -1
                name = hexToASCII(encoded_hex_data[cur_index+8:cur_index+16])
                size = box_size(encoded_hex_data[cur_index:cur_index+8])
                print("Looking for avcC in: " + name)
                count = 0

                while (count < size*2):
                    name = hexToASCII(encoded_hex_data[cur_index:cur_index+8])

                    if (name == "avcC"):
                        count = size*2
                        print("Found avcC")
                        avcc_index = cur_index

                    cur_index += 1
                    count += 1

                #8-16 is config, 16-18 is FF, 18-20 is no_sps
                #print(str(encoded_hex_data[avcc_index+18:avcc_index+20]))
                no_sps = box_size(encoded_hex_data[avcc_index+18:avcc_index+20]) - 224
                count = 0
                sps_index = avcc_index+20
                sps_data = None
                
                while (count < no_sps):
                    size = box_size(encoded_hex_data[sps_index:sps_index+4])
                    data = str(encoded_hex_data[sps_index+4:sps_index+4+size*2])
                    sps_data = bytearray(bytes.fromhex(data))
                    print("SPS #" + str(count+1) + " has data: " + data + " and size: " +str(size))
                    sps_index += 4+size*2
                    count += 1

                no_pps = box_size(encoded_hex_data[sps_index:sps_index+2])
                #print(no_pps)
                count = 0
                pps_index = sps_index+2
                pps_data = None

                while (count < no_pps):
                    size = box_size(encoded_hex_data[pps_index:pps_index+4])
                    data = str(encoded_hex_data[pps_index+4:pps_index+4+size*2])
                    pps_data = bytearray(bytes.fromhex(data))
                    print("PPS #" + str(count+1) + " has data: " + data + " and size: " +str(size))
                    pps_index += 4+size*2
                    count += 1

                #test
                #print("SPS: " + str(sps_data))
                #print("PPS: " + str(pps_data))

                #4.2) the NAL frames need to be reconstructed
                # frames should be segmented using NAL start codes 00 00 00 01

                #print(key_frames) #1,92,183,274,365 my test data at least
                #need to inset a strt cd, sps, strt cd, pps, strt cd, nal ...

                #each sample is 4 bytes nal length X bytes nal, repeated, i think
                annexb_out = bytearray() #append with += bytearray(cur_bytes)
                start_code = bytearray(bytes.fromhex("00000001"))
                #for each sample
                cur_sample = 0

                while (cur_sample < len(samples)):
                    #is that sample a key frame?
                    count = 0

                    while (count < len(key_frames)):
                        #5) insert SPS and PPS
                        #if so add the strt cd sps and strt cd pps
                        if (cur_sample + 1 == key_frames[count]):
                            #print("Wowser a key frame!") #... Let me have my whimsical tests
                            annexb_out += start_code + sps_data + start_code + pps_data

                        count += 1

                    #until we reach the end of the file
                    count = 0

                    #this is continued in terms of hex for clarity
                    hex_sample = samples[cur_sample].hex()

                    while (count < len(hex_sample)):
                        #read the first 4 bytes, this is the length X
                        length = box_size(hex_sample[count:count+8]) #length in bytes, can be odd
                        nal = hex_sample[count+8:count+length*2] #1 byte is 2 hex chars so double
                        annexb_out += start_code + bytearray(bytes.fromhex(nal))#append strt cd + nal to the output 
                        count += length*2

                    cur_sample += 1

                print(annexb_out)

                #6) Decode the video stream (use a decoder for the love of god)
                #now the data os in annexb h264decoder can read it
                #figure out how it works, how it take in info and what to provide it
                #need the following: import h264decoder import numpy as np from PIL import Image
                #get the decoder h264decoder.H264decoder()
                #get frames by decoder.decode(annexb_out)
                #for frame_data in frames:
                #    (data, w, h, ls) = frame_data
                #    if data:
                #        # Convert the raw bytes to a Pillow Image
                #        img = Image.frombytes('RGB', (w, h), data)
                #        img.save("output.jpg")

                #7) Reconstruct the frames into BMP

        else:
            print("Failed to find all five required boxes: stsd, stts, stsc, stsz and stco")



#print("Hello world")
#print("Only mp4 files are acceptable not fmp4")
#video_target = "cat.mp4"
#read_file(video_target)
