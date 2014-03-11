from flask import Flask, render_template, abort
import os
import config
import math
from datetime import datetime
app = Flask(__name__)

# index
@app.route("/")
def hello():
    return render_template('home.tpl')

# get a list of all logs
def bat_logs():
    bat_logs_dirlist = os.listdir(config.bats_log_path)
    bat_logs_list={}
    for bat_logfile in bat_logs_dirlist:
        bat_log = {}
        bat_log.update({'filename': bat_logfile})
        bat_log.update({'date': datetime.strptime(bat_logfile[14:], "%Y-%m-%d")})
        bat_logs_list.update({bat_logfile[14:]: bat_log})
    return bat_logs_list

# return the human-readable name of a bit
def get_bit_name(bit):
    # first half of bits are side A, the other bits are side B
    if bit>=(config.num_beams/2):
        return "B%.2d" % (bit-(config.num_beams/2-1)+1)
    else:
        return "A%.2d" % (bit+1)

# calculate flippy (and sticky) bits (for bat-logfiles)
def get_flippy_bits(bat_logfile_rows):
    # initialise some lists
    flippy_bits = [] # used at the end, contains flippy (and sticky) bits
    single_flip_counters = [] # count times a bit flipped without keeping the value for a longer time (< 3 samples)
    tmp_counters = [] # temporary counter to count how many samples a bit stayed the same value
    bit_counters = [] # count how often a bit is 1 (interrupted or - tested in this case - maybe not working correctly)
    first = True # first row is used to fill lastrow_bits, need some kind of marker
    valid_lines = 0 # count valid lines (excluding error messages about the arduino not working correctly)

    # set up our lists
    for pos in range(50):
        single_flip_counters.append(0)
        tmp_counters.append(0)
        bit_counters.append(0)

    # for every row in the logfile
    for row in bat_logfile_rows:
        # skip over uninteresting rows (error messages)
        if row[26] != 'T' and row[26] != 'I':
            continue
        # get bits from line
        row_bits = list(row[45:])
        if not first:
            for pos in range(50):
                # if bit is high increment bit_counter (testing for sticky bits)
                if row_bits[pos] == '1':
                    bit_counters[pos] += 1
                # if the bit is the same value as last time increment the temporary counter (testing for flippy bits)
                if lastrow_bits[pos] == row_bits[pos]:
                    tmp_counters[pos] += 1
                # if the value changed and didn't stay for at least 3 samples increment the single_flip_counter for this bit
                elif tmp_counters[pos] < 3:
                    single_flip_counters[pos] += 1
                    tmp_counters[pos] = 0
                # if the value changed but stayed at least 3 samples we reset the temporary counter to zero
                else:
                    tmp_counters[pos] = 0
        else:
            first = False
        lastrow_bits = row_bits
        valid_lines += 1

    # for every bit
    for pos in range(50):
        # test if the bit flipped a lot of times (makes it a flippy bit)
        if single_flip_counters[pos] > 20:
            flippy_bits.append(pos)
        # test if the bit stayed high a long time (1/2 of the time)
        if bit_counters[pos] > valid_lines / 2 and not pos in flippy_bits:
            flippy_bits.append(pos)
    return flippy_bits

# parse bat-logfile
def bat_log_content(bat_log):
    # read logfile (we need no error handling, everything will work! i guess..)
    rows = open("%s/%s" % (config.bats_log_path, bat_log['filename']),"r").read().split("\n")[:-1]
    # get (probable) flippy bits
    flippy_bits = get_flippy_bits(rows) 
    # first line just initialises values like lastrow and lasttime, we need some kind of marker for this
    first = True 
    lasttime = 9999999999999999 # dirty "hack", saves a few rows of code :)
    # collect a block (for guessing of direction)
    begin_block = 0
    block = []
    # direction-guess-counters
    A_to_B = 0
    B_to_A = 0
    WAT = 0
    # initialise content-"buffer"
    content = ""
    for row in rows:
        # only valid rows are interesting
        if row[26] != 'T' and row[26] != 'I':
            continue
        row_bits = list(row[45:])
        # try to correct flippy and sticky bits and colorify everything
        for bit in range(50):
            if bit in flippy_bits:
                row_bits[bit] = 0
        raw_row_bits = row_bits[:]
        for bit in range(50):
            if bit in flippy_bits:
                # if the flippy bit is at the top or bottom just take the value of the bit next to it
                if bit == 0:
                    row_bits[bit] = '<span class="flippy">%s</span>' % raw_row_bits[bit+1]
                elif bit == (config.num_beams/2)-1:
                    row_bits[bit] = '<span class="flippy">%s</span>' % raw_row_bits[bit-1]
                elif bit == config.num_beams/2:
                    row_bits[bit] = '<span class="flippy">%s</span>' % raw_row_bits[bit+1]
                elif bit == config.num_beams-1:
                    row_bits[bit] = '<span class="flippy">%s</span>' % raw_row_bits[bit-1]
                # if the flippy bit is between two interrupted beams, it's probably interrupted too
                elif raw_row_bits[bit-1] == '1' and raw_row_bits[bit+1] == '1':
                    row_bits[bit] = '<span class="flippy">1</span>'
                # if just one bit next to the flippy bit is interrupted we have to do some guessing...
                elif (raw_row_bits[bit-1] == '1' or raw_row_bits[bit+1] == '1'):
                    # A
                    if bit < ((config.num_beams/2)-1):
                        if raw_row_bits[0:((config.num_beams/2)-1)].count('1') > 2:
                            row_bits[bit] = '<span class="flippy">1</span>'
                        else:
                            row_bits[bit] = '<span class="zero">0</span>'
                    # B
                    else:
                        if raw_row_bits[config.num_beams/2:config.num_beams-1].count('1') > 2:
                            row_bits[bit] = '<span class="flippy">1</span>'
                        else:
                            row_bits[bit] = '<span class="zero">0</span>'
                # if nothing around the flippy bit is interrupted we can assume that it just flipped -> 0
                else:
                    row_bits[bit] = '<span class="zero">0</span>'
            # colorify normal bits
            elif row_bits[bit] == '0':
                row_bits[bit] = '<span class="zero">0</span>'
            else:
                row_bits[bit] = '<span class="one">1</span>'
        # put row together
        row = "%s%s %s" % (row[:45], "".join(row_bits[0:((config.num_beams/2)-1)]), "".join(row_bits[(config.num_beams/2):(config.num_beams-1)]))
        # if there were any changes throw the row at the user
        if not first and row[45:] != lastrow[45:] and row[45:].count('1')>1:
            time = int(row[28:44])
            if (time - lasttime) > 3e6: # if over 3 seconds nothing happened we can assume that there is no bat inside
                # try to guess what happened in this block
                interrupts = {'A': [], 'B': []}
                for line in block:
                    interrupts['A'].append(line[0:((config.num_beams/2)-1)].count('1'))
                    interrupts['B'].append(line[(config.num_beams/2):(config.num_beams-1)].count('1'))
                # if an object takes longer than 1 second inside the system it's probably not a flying bat...
                if lasttime - begin_block > 1e6:
                    from_to = "??????"
                    WAT+=1
                # if we have to little data to work with we can't really say anything about the direction
                elif sum(interrupts['A']) < 4 or sum(interrupts['B']) < 4:
                    from_to = "??????"
                    WAT+=1
                # blocks in the middle, probably just a turnaround inside the system
                elif interrupts['A'][0] == 0 and interrupts['A'][-1] == 0:
                    from_to = "??????"
                    WAT+=1
                elif interrupts['B'][0] == 0 and interrupts['B'][-1] == 0:
                    from_to = "??????"
                    WAT+=1
                # block begins at B, nothing on A-side, probably moving from B to A
                elif interrupts['A'][0] == 0 and interrupts['B'][0] != 0:
                    from_to = "B -> A"
                    B_to_A+=1
                # same thing other way around
                elif interrupts['B'][0] == 0 and interrupts['A'][0] != 0:
                    from_to = "A -> B"
                    A_to_B+=1
                # same but from the end of the block (which side is free first)
                elif interrupts['A'][-1] == 0 and interrupts['B'][-1] != 0:
                    from_to = "A -> B"
                    A_to_B+=1
                elif interrupts['B'][-1] == 0 and interrupts['A'][-1] != 0:
                    from_to = "B -> A"
                    B_to_A+=1
                # everything else is not that easy to guess
                else:
                    from_to = "??????"
                    WAT+=1
                # reset block
                block = []
                # print time difference and guessed direction
                diff = ((time-lasttime)/1000000.0)
                content += '<span class="seperator">'
                if diff < 60:
                    content += "--- %d Sekunden Ruhe (Letzter Block: %s) ---\n" % (diff, from_to)
                else:
                    seconds = diff % 60
                    content += "--- %d:%.2d Minuten Ruhe (Letzter Block: %s) ---\n" % (math.floor(float(diff)/60.0), seconds, from_to)
                content += '</span>'
            lasttime = time
            content += "%s\n" % row
            if len(block) == 0:
                begin_block = time
            block.append(raw_row_bits)
        if first:
            first = False
        lastrow = row

    header = "Flippy Bits: %s\nA -> B: %d\nB -> A: %d\n??????: %d\n" % (', '.join(get_bit_name(x) for x in flippy_bits), A_to_B, B_to_A, WAT)
    header+= "                                             Innen (A)%sAu&szlig;en (B)" % "".ljust(config.num_beams/2-9)
    return "%s\n%s" % (header, content)

# get list of all bat-logs
@app.route("/bats/")
def bat_logs_view():
    title = "/bats/"
    return render_template('bats/loglist.tpl', bat_logs_list=sorted(bat_logs().iteritems(), reverse=True), title=title)

# get list of bat-logs in a year
@app.route("/bats/<int:year>/")
def bat_logs_year_view(year):
    selected_items={}
    for date, bat_log in bat_logs().iteritems():
        if date[0:4] == "%.4d" % year:
            selected_items[date] = bat_log
    title = "%.4d" % year
    h1 = '/<a href="/bats/">bats</a>/'
    h1+= '%.4d' % year
    return render_template('bats/loglist.tpl', bat_logs_list=sorted(selected_items.iteritems(), reverse=True), title=title, h1=h1)

# get list of bat-logs in a month
@app.route("/bats/<int:year>/<int:month>/")
def bat_logs_month_view(year,month):
    selected_items={}
    for date, bat_log in bat_logs().iteritems():
        if date[0:7] == "%.4d-%.2d" % (year, month):
            selected_items[date] = bat_log
    title = "%.4d-%.2d" % (year, month)
    h1 = '/<a href="/bats/">bats</a>/'
    h1+= '<a href="/bats/%.4d/">%.4d</a>/' % (year, year)
    h1+= '%.2d/' % (month)
    return render_template('bats/loglist.tpl', bat_logs_list=sorted(selected_items.iteritems(), reverse=True), title=title, h1=h1)

# get bat-log of a specific day (including content and statistics)
@app.route("/bats/<int:year>/<int:month>/<int:day>")
def bat_log_view(year,month,day):
    bat_logs_list = bat_logs()
    if not "%.4d-%.2d-%.2d" % (year,month,day) in bat_logs_list:
        abort(404)

    bat_log = bat_logs_list["%.4d-%.2d-%.2d" % (year,month,day)]
    h1 = '/<a href="/bats/">bats</a>/'
    h1+= '<a href="/bats/%.4d/">%.4d</a>/' % (year, year)
    h1+= '<a href="/bats/%.4d/%.2d/">%.2d</a>/' % (year, month, month)
    h1+= '%.2d' % day
    title = "%.4d-%.2d-%.2d" % (year,month,day)
    return render_template('bats/log.tpl', bat_log_content=bat_log_content(bat_log), title=title, h1=h1)

if __name__ == "__main__":
    import config
    app.secret_key = config.secret_key
    app.debug = config.debug
    app.run()
