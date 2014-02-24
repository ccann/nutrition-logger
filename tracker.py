#!/usr/bin/env python
## item <name> -- <amount> <units> <cals> <fat> <carbs> <protein>
## db <name> -- <amount> <units>

# TODO:
# fix Cups
# make the fridge just track the units and take anything and then convert it? What's the best way to handle this



import os
import sys
import datetime
import string
import logging
import smtplib
logging.basicConfig(filename='tracker.log',level=logging.DEBUG)

email = 'cocanning11@gmail.com'
grams = ['g', 'grams', 'gram']
cups = ['c', 'cups', 'cup']
ounces = ['oz', 'ounces', 'ounce']

class Food:
    def __init__(self, n, cl, f, cr, p):
        self.name = n
        self.cals = float(cl)
        self.fat = float(f)
        self.carbs = float(cr)
        self.protein = float(p)

    def __repr__(self):
        return '%s  -->  cals: %.1f  |  fat: %.1f  |  carbs: %.1f  |  protein: %.1f'\
            %(self.name,self.cals,self.fat,self.carbs,self.protein)

def read_fridge(fp):
    """read the fridge at fp into a dictionary"""
    try:
        with open(fp, 'r+') as fridge:
            foods = {}
            for line in fridge:
                l = line.split(',')
                foods[l[0]] = Food(l[0],l[1],l[2],l[3],l[4])
            return foods
    except IndexError:
        print("rotten food in fridge: check the format of your fridge entries")
    except IOError as e:
        print 'warning: %s not found, creating a new empty fridge' %fp
        return {}

def stock_fridge(fp, new_foods):
    """write the new_foods dict to the fridge at fp"""
    with open(fp, 'a+') as fridge:
        for f in new_foods:
            fridge.write('%s,%.1f,%.1f,%.1f,%.1f\n' %(f.name, f.cals, f.fat, f.carbs, f.protein))
            
def to_serving(amount, units, cals, fat, carbs, protein):
    """returns the nutrition facts on the order of 100 grams"""
    if units in ounces:
        amount = to_standard(amount, units)
        d = float(100.0/float(amount))
        return d*cals, d*fat, d*carbs, d*protein
    elif units in grams:
        #print "%s, %s, %s, %s, %s" %(amount, cals, fat, carbs, protein)
        d = float(100.0/float(amount))
        return d*cals, d*fat, d*carbs, d*protein
    elif units in cups:
        d = float(1.0/float(amount))
        return d*cals, d*fat, d*carbs, d*protein
    else:
        raise ValueError

def to_standard(amount, units):
    """returns amount in grams or cups"""
    if units.replace('.','') in ounces:
        return float(amount)*28.3495 ## convert to grams
    else:
        return float(amount)

def log_item(fp, new_foods, s):
    """standardizes item s and appends it to file at fp, return updated new_foods dict"""
    s = s.split('--')
    name = s[0].strip()
    rest = s[1].split()
    rest[2:] = map(float, rest[2:])
    print('about to log: %s' %rest)
    with open(fp, 'a+') as today:
        today.write('%s,%.1f,%.1f,%.1f,%.1f\n' %(name, rest[2], rest[3], rest[4], rest[5]))
    amount = to_standard(rest[0], rest[1])

    cals, fat, carbs, protein = to_serving(amount, rest[1], rest[2], rest[3], rest[4], rest[5])
    new_foods[name] = Food(name, cals, fat, carbs, protein)
    return new_foods

## desc, amount, units
def log_db(fp, foods, s):
    print(s)
    s = s.split('--')
    name = s[0].strip()
    rest = s[1]
    s = rest.split()
    amount = to_standard(s[0], s[1])
    f = foods.get(name)
    print(f)
    if f:
        d = float(float(amount)/100.0)
        print(d)
        with open(fp, 'a+') as today:
            today.write('%s,%.1f,%.1f,%.1f,%.1f\n'\
                        %(name, float(d*f.cals), float(d*f.fat), float(d*f.carbs), float(d*f.protein)))
    else:
        print('%s not in the fridge' %name)

def send_email(message):
    gmail_user = "dailynutrition0903@gmail.com"
    gmail_pwd = "Lucy09032009"
    FROM = 'dailynutrition0903@gmail.com'
    TO = [email] #must be a list
    SUBJECT = "Daily Nutrition Update"
    TEXT = message
    msg = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the email!'
    except Exception as e:
        print "failed to send mail: %s" %e

def summarize_today(fp):
    with open(fp, 'r') as today:
        s = ''
        for line in today:
            l = line.split(',')
            f = Food(l[0], l[1], l[2], l[3], l[4])
            s = s + str(f) + '\n'
    return s

def main():
    home = os.path.expanduser('~')
    db_dir = os.path.join(home,'.logs')
    fridge_path = os.path.join(db_dir,'fridge.csv')
    year = str(datetime.date.today().year)
    month = str(datetime.date.today().month)
    day = str(datetime.date.today().day)
    today_path = os.path.join(db_dir, 'entry_%s_%s_%s' %(year, month, day))
    txt = ''
    foods = read_fridge(fridge_path)
    new_foods = {}

    while txt != 'exit':
        try:
            txt = raw_input('-> ').lower()
            if string.find(txt.strip(),'item') == 0:
                new_foods = log_item(today_path, new_foods, txt.replace('item', '').strip())
            elif string.find(txt.strip(),'db') == 0:
                log_db(today_path, foods, txt.replace('db','').strip())
            elif txt == 'fridge':
                for v in foods.values(): print v
            elif txt == 'today':
                print(summarize_today(today_path))
            elif txt == 'email':
                send_email(summarize_today(today_path))

        except IndexError:
            print "formats: item <food_description> -- <amount> <units> <cals> <fat> <carbs> <protein>"
            print "         db <food_description> -- <amount> <units>\n"
        except IOError as e:
            print 'File not found: %s' %e

if __name__=='__main__':
    main()
    
    # if s[1] == 'db':
    #     try:
    #         name = ''.join(s[1].split('_')).lower()
    #         units = s[3].lower()
    #         amount = to_standard_amount(float(s[2]), units)
            
    #         f = open('fridge.csv', 'r')
    #         if name in line.lower():
    #             l = line.split(',')
    #             standardize(
    #             today.write('%s,%s,%s,%s,%s,%s,%s\n' %(name,amount,cals,fat,carbs,protein))
    #     except IndexError:
    #         

    
## email daily summary
