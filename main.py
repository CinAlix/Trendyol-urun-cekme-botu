import requests
import json
from loguru import logger
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'origin': 'https://www.trendyol.com',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}

params = {
    'mid': '968',
    'os': '1',
    'pi': '1',  # Sayfa numarası, başta 1 olarak ayarlanır
    'culture': 'tr-TR',
    'userGenderId': '2',
    'pId': '0',
    'isLegalRequirementConfirmed': 'false',
    'searchStrategyType': 'DEFAULT',
    'productStampType': 'TypeA',
    'scoringAlgorithmId': '2',
    'fixSlotProductAdsIncluded': 'true',
    'searchAbDecider': 'CA_B,SuggestionTermActive_B,AZSmartlisting_62,BH2_B,Suggestion_A,MB_B,FRA_2,MRF_1,ARR_B,BrowsingHistoryCard_A,SP_B,PastSearches_B,SearchWEB_13,SuggestionJFYProducts_B,SDW_23,SuggestionQF_B,BSA_D,BadgeBoost_A,CatTR_B,Relevancy_1,FilterRelevancy_1,Smartlisting_65,SuggestionBadges_B,ProductGroupTopPerformer_B,OpenFilterToggle_2,RF_1,CS_1,RR_2,BS_2,SuggestionPopularCTR_B',
    'location': 'null',
    'channelId': '1',
}

def read_lc_values(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def fetch_products(mid, lc_value):
    params['mid'] = mid
    params['lc'] = lc_value
    product_info = []
    page_number = 1
    
    while True:
        logger.success(f"{mid} İd li satıcıdan {lc_value} Ürünleri çekiliyor. {page_number} Sayfa Ürün Çekildi")
        params['pi'] = str(page_number)
        response = requests.get(
            'https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr',
            params=params,
            headers=headers,
        )
        
        # Check if response status is not 200
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            break
        
        try:
            parsed_data = response.json()
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON response")
            break
        
        # Check if 'result' and 'products' are in the parsed_data
        if 'result' not in parsed_data or 'products' not in parsed_data['result']:
            print("Error: Unexpected response format")
            break
        
        products = parsed_data['result']['products']
        
        if not products:
            break
        
        for product in products:
            name = product['name']
            price = product['price']['sellingPrice']
            url = product['url']
            product_id = product["id"]
            product_info.append({
                "id": product_id,
                "link": "https://www.trendyol.com" + url,
                "productTitle": name,
                "convertedPrice": price
            })
        
        page_number += 1
    
    return product_info

def main():
    lc_lines = read_lc_values('ürün.txt')
    all_products = {}
    
    for line in lc_lines:
        mid, lc_values = line.split(':')
        products = fetch_products(mid, lc_values)
        all_products[line] = products
    
    # Tüm ürünleri json dosyasına kaydet
    with open('urunler.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=4)
    
    logger.success(f"{len(lc_lines)} lc değeri kullanılarak toplamda {sum(len(products) for products in all_products.values())} ürün başarıyla çekildi ve urunler.json dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
