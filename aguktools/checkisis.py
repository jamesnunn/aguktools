import argparse



def check_isis_banks(isis_string):
    sections = isis_string.split('SECTION')[1:]

    messages = []

    for section_block in sections:
        data = section_block.split('\n')
        sec_id = data[1]

        left_seen, right_seen = False, False

        for row in data:
            if 'left' in row:
                if left_seen:
                    messages.append('{} contains multiple LB'.format(sec_id))
                left_seen = True
                if right_seen:
                    messages.append('{} RB found before LB'.format(sec_id))

            if 'right' in row:
                if right_seen:
                    messages.append('{} contains multiple RB'.format(sec_id))
                right_seen = True

        if not left_seen:
            messages.append('{} missing LB'.format(sec_id))

        if not right_seen:
            messages.append('{} missing RB'.format(sec_id))

    return sorted(list(set(messages)), reverse=True)



def cli_main():
    parser = argparse.ArgumentParser('checkthisisisis')
    parser.add_argument('infile')
    args = parser.parse_args()

    path = args.infile

    with open(path) as isisfile:
        messages = check_isis_banks(isisfile.read())

    print('\n'.join(messages))