import configparser as cf
setup = cf.ConfigParser()
setup.read("Bot_Config.ini")
CEX_NameNotify = setup.get("User_Info","CEX_Name")

#Set date
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

#set line notify
Line_Token = setup.get("User_Info","Line_Token")
import requests
Line_notice_start = ['\nPopier v1 bot = START \n'+ 'Running on - ' + CEX_NameNotify + '\n' + dt_string + '\nCr.Popier']
#############################################################################################
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': f'Bearer {Line_Token}'
}
url = 'https://notify-api.line.me/api/notify'
message = Line_notice_start
print(headers)
r = requests.post(url=url, headers=headers, data={'message': message})
#############################################################################################

#start loop
#while True:
#   try:
import ccxt
apiKey = setup.get("User_Info","Api_Key")
secret = setup.get("User_Info","Api_Secret")
password  = setup.get("User_Info","Api_password") 
Account_name  = setup.get("User_Info","CEX_Account_name") 
CEX_Name = setup.get("User_Info","CEX_Name")
Coin1 = setup.get("User_Info","Coin1")
Coin_Base = setup.get("User_Info","Coin_Base")
Rebalance_percent = setup.getfloat("User_Info","Rebalance_percent")
Loop_Run = setup.getint("User_Info","Loop_Run")
Min_size = setup.getfloat("User_Info","Minimum_Order_Base_Unit")
#Setup pair name
Pair1 = Coin1+'/'+Coin_Base
Pair2 = Coin_Base+'/'+"USDT"

#Login
if CEX_Name == "gateio" :
   exchange = ccxt.gateio  ({'apiKey' : apiKey ,'secret' : secret ,'password' : password ,'enableRateLimit': True})
elif CEX_Name == "binance" :
   exchange = ccxt.binance ({'apiKey' : apiKey ,'secret' : secret ,'password' : password ,'enableRateLimit': True})
elif CEX_Name == "ftx" :
   exchange = ccxt.ftx ({'apiKey' : apiKey ,'secret' : secret ,'password' : password ,'enableRateLimit': True})
elif CEX_Name == "bitfinex" :
   exchange = ccxt.bitfinex ({'apiKey' : apiKey ,'secret' : secret ,'password' : password ,'enableRateLimit': True})

exchange.cancel_all_orders(Pair1) 

while True:
   try:
      # Check Balance in account
      Get_balance = exchange.fetch_balance()

      # Check asset that need to run bot (unit)
      Asset_01 = Get_balance [Coin1] ['total']
      Asset_02 = Get_balance [Coin_Base] ['total']
      print("Asset 01 = " , Asset_01,Coin1)
      print("Asset 02 = " , Asset_02,Coin_Base)

      # Get price to check value
      get_price_asset_01 = exchange.fetch_ticker(Pair1) 
      get_price_asset_02 = exchange.fetch_ticker(Pair2)

      last_price_01 = get_price_asset_01 ['last']
      ask_price_01 = get_price_asset_01['ask']
      bid_price_01 = get_price_asset_01['bid']
      print("Last_price_01 = " ,last_price_01)
      print("Ask_price_01 = ",ask_price_01)
      print("Bid_price_01 = ",bid_price_01)

      last_price_02 = get_price_asset_02 ['last']
      print("Last_price_02 = " ,last_price_02)

      # Cal asset value (usd)
      Asset_01_Value = Asset_01 * last_price_01
      print("Asset_01_Value = " ,Asset_01_Value, Coin_Base)

      Asset_02_Value = Asset_02 * 1
      print("Asset_02_Value = " ,Asset_02_Value, Coin_Base)

      #Check pending order
      Check_order_pending = exchange.fetch_open_orders(Pair1)
      Count_pending = len(Check_order_pending)
      print('Total pending = ', Count_pending, ' Order')

      # Main rebalancing bot
      # Rebalance_mark (Find avaerage balance for rebalance referent point)
      Rebalance_mark = ((Asset_01_Value + Asset_02_Value)/2)
      Percent_asset = ((abs(Asset_01_Value-Rebalance_mark))/Asset_02_Value)*100

      if Asset_01_Value > (Rebalance_mark + ((Rebalance_mark * Rebalance_percent/100))) :
         print("Asset_01_Value ",Asset_01_Value ,">", (Rebalance_mark + (Rebalance_mark*Rebalance_percent/100)))
         print("SELL")
         diff_sell = Asset_01_Value - Rebalance_mark
         sell_amount = (diff_sell/last_price_01)
         print(diff_sell)
         print(sell_amount)

         if diff_sell > Min_size:
            exchange.cancel_all_orders(Pair1) 
            print('Cancel all order on ', Pair1)
            #############################################################################################
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {Line_Token}'
            }
            url = 'https://notify-api.line.me/api/notify'
            message = ('Cancel all order...')
            print(headers)
            r = requests.post(url=url, headers=headers, data={'message': message})
            #############################################################################################
            if CEX_Name == "gateio" :
               exchange.create_limit_sell_order(Pair1, amount=sell_amount, price=bid_price_01)
            else :
               exchange.create_order(Pair1, 'market', 'sell', amount=sell_amount, price=last_price_01)
            Line_notice1 = ['\n Popier v1 bot = Sell ' + Pair1 + '\n Sell amount =' + '%.2f' % sell_amount + Coin1]
            #############################################################################################
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {Line_Token}'
            }
            url = 'https://notify-api.line.me/api/notify'
            message = Line_notice1
            print(headers)
            r = requests.post(url=url, headers=headers, data={'message': message})
            #############################################################################################

         else:
            print("Popier v1 bot = Don't meet minimum requirement Cannot SELL...Please wait...")

      elif Asset_01_Value < (Rebalance_mark - ((Rebalance_mark*Rebalance_percent/100))) :
         print("Asset_01_Value ",Asset_01_Value ,"<", (Rebalance_mark - (Rebalance_mark*Rebalance_percent/100) ))
         print("Buy")
         diff_buy  = Rebalance_mark - Asset_01_Value
         buy_amount = (diff_buy/last_price_01)
         print(diff_buy)
         print(buy_amount)

         if diff_buy > Min_size:
            exchange.cancel_all_orders(Pair1) 
            print('Cancel all order on ', Pair1)
            #############################################################################################
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {Line_Token}'
            }
            url = 'https://notify-api.line.me/api/notify'
            message = ('Cancel all order...')
            print(headers)
            r = requests.post(url=url, headers=headers, data={'message': message})
            #############################################################################################
            if CEX_Name == "gateio" :
               exchange.create_limit_buy_order(Pair1, amount=buy_amount, price=ask_price_01)
            else :
               exchange.create_order(Pair1, 'market', 'buy', amount=buy_amount, price=last_price_01)
            Line_notice2 = ['\n Popier v1 bot = Buy ' + Pair1 + '\n Buy amount =' + '%.2f' % buy_amount + Coin1]
            #############################################################################################
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {Line_Token}'
            }
            url = 'https://notify-api.line.me/api/notify'
            message = Line_notice2
            print(headers)
            r = requests.post(url=url, headers=headers, data={'message': message})
            #############################################################################################

         else:
            print(print("Popier v1 bot = Don't meet minimum requirement Cannot BUY...Please wait..."))
            
      else :
         print("%Difference = ",((abs(Asset_01_Value-Rebalance_mark))/Asset_01_Value)*100,"%")
         print("No Trade")

###################################################################################################################################
      #Calculation pending order
      if Count_pending != 2 :
         exchange.cancel_all_orders(Pair1) 
         print('Set New Pending...')

         Rebalance_mark_mid = ((Asset_01_Value + Asset_02_Value)/2)
         Fair_price_mid = Rebalance_mark_mid / Asset_01
         print('Middle price = ',Fair_price_mid)

         Rebalance_mark_up = Rebalance_mark_mid + (Rebalance_mark_mid * Rebalance_percent/100)
         Fair_price_up = Rebalance_mark_up / Asset_01
         Diff_sell_pending = Rebalance_mark_up - Rebalance_mark_mid
         Sell_pending_amount = Diff_sell_pending/Fair_price_up
         if Diff_sell_pending > Min_size:
            exchange.create_limit_sell_order(Pair1, amount=Sell_pending_amount, price=Fair_price_up)
            if Fair_price_up < 0.00001:
               Fair_price_up_Str = str(f'{Fair_price_up:.8f}')
            elif Fair_price_up < 0.0001 and Fair_price_up > 0.00001:
               Fair_price_up_Str = str(f'{Fair_price_up:.7f}')
            elif Fair_price_up < 0.001 and Fair_price_up > 0.0001:
               Fair_price_up_Str = str(f'{Fair_price_up:.6f}')
            elif Fair_price_up < 0.01 and Fair_price_up > 0.001:
               Fair_price_up_Str = str(f'{Fair_price_up:.5f}')
            elif Fair_price_up < 0.1 and Fair_price_up > 0.01:
               Fair_price_up_Str = str(f'{Fair_price_up:.4f}')
            elif Fair_price_up < 1 and Fair_price_up > 0.1:
               Fair_price_up_Str = str(f'{Fair_price_up:.3f}')
            else:
               Fair_price_up_Str = str(f'{Fair_price_up:.2f}')
            Notice_pending1 = ['\nSet new pending_SELL ' + Pair1 + '\nSell_amount =' + '%.2f' % Sell_pending_amount + Coin1 + '\nPlace order @' + Fair_price_up_Str]
            #############################################################################################
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {Line_Token}'
            }
            url = 'https://notify-api.line.me/api/notify'
            message = Notice_pending1
            print(headers)
            r = requests.post(url=url, headers=headers, data={'message': message})
            #############################################################################################
         print('Set upper = ', Fair_price_up)
         print('Diff sell =', Diff_sell_pending, Coin_Base)
         print('Sell pending amount = ', Sell_pending_amount, Coin1)

         Rebalance_mark_down = Rebalance_mark_mid - (Rebalance_mark_mid * Rebalance_percent/100)
         Fair_price_down = Rebalance_mark_down / Asset_01
         Diff_buy_pending = Rebalance_mark_mid - Rebalance_mark_down
         Buy_pending_amount = Diff_buy_pending/Fair_price_down
         if Diff_sell_pending > Min_size:
            exchange.create_limit_buy_order(Pair1, amount=Buy_pending_amount, price=Fair_price_down)
            if Fair_price_down < 0.00001:
               Fair_price_down_Str = str(f'{Fair_price_down:.8f}')
            elif Fair_price_down < 0.0001 and Fair_price_down > 0.00001:
               Fair_price_down_Str = str(f'{Fair_price_down:.7f}')
            elif Fair_price_down < 0.001 and Fair_price_down > 0.0001:
               Fair_price_down_Str = str(f'{Fair_price_down:.6f}')
            elif Fair_price_down < 0.01 and Fair_price_down > 0.001:
               Fair_price_down_Str = str(f'{Fair_price_down:.5f}')
            elif Fair_price_down < 0.1 and Fair_price_down > 0.01:
               Fair_price_down_Str = str(f'{Fair_price_down:.4f}')
            elif Fair_price_down < 1 and Fair_price_down > 0.1:
               Fair_price_down_Str = str(f'{Fair_price_down:.3f}')
            else:
               Fair_price_down_Str = str(f'{Fair_price_down:.2f}')
            Notice_pending2 = ['\nSet new pending_BUY ' + Pair1 + '\nBuy_amount =' + '%.2f' % Buy_pending_amount + Coin1 + '\nPlace order @' + Fair_price_down_Str]
            #############################################################################################
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {Line_Token}'
            }
            url = 'https://notify-api.line.me/api/notify'
            message = Notice_pending2
            print(headers)
            r = requests.post(url=url, headers=headers, data={'message': message})
            #############################################################################################
         print('Set lower = ', Fair_price_down)
         print('Diff buy = ', Diff_buy_pending, Coin_Base)
         print('Buy pending amount = ', Buy_pending_amount, Coin1)
########################################################################################################################################
      import time
      sleep = Loop_Run
      print("Sleep",sleep,"sec.\n")
      time.sleep(sleep) 
                                      
   except:
      #############################################################################################
      headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': f'Bearer {Line_Token}'
      }
      url = 'https://notify-api.line.me/api/notify'
      message = ("Bot Stopped...Please Check...")
      print(headers)
      r = requests.post(url=url, headers=headers, data={'message': message})
      #############################################################################################