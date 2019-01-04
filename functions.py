from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi
import pandas as pd
import datetime
from config import access_token, page_id, ad_account_id, instagram_id

init = FacebookAdsApi.init(access_token=access_token)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def get_insights(_level='ad', _days=30, _campaign_id=None, _ad_account=ad_account_id):
    from facebook_business.adobjects.adsinsights import AdsInsights
    # init = FacebookAdsApi.init(access_token=access_token)
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    date_1 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    start_date = date_1 - datetime.timedelta(days=_days)
    start_date = start_date.strftime("%Y-%m-%d")
    if _level == 'ad':
        fields = [
            'campaign_id',
            'campaign_name',
            'adset_id',
            'adset_name',
            'ad_id',
            'ad_name',
            'reach',
            'impressions',
            'frequency',
            'spend',
            'clicks',
            'cpp',
            'cpm',
            'relevance_score',
            'actions'
        ]
        if _campaign_id is None:
            params = {
                'level': 'ad',
                # 'action_attribution_windows': ['1d_click', '1d_view'],
                # 'filtering': [{'field':'delivery_info','operator':'IN','value':['active','limited']}],
                # 'breakdowns': ['age'],
                'time_range': {'since': start_date, 'until': end_date},
            }
        else:
            params = {
                'level': 'ad',
                # 'action_attribution_windows': ['1d_click', '1d_view'],
                # 'filtering': [{'field':'delivery_info','operator':'IN','value':['active','limited']}],
                'filtering': [{'field':'campaign.id', 'operator':'IN', 'value':[_campaign_id]}],
                # 'breakdowns': ['age'],
                'time_range': {'since': start_date, 'until': end_date},
            }
        sort_values = ['campaign_name', 'adset_name', 'ad_name']
    elif _level == 'adset':
        fields = [
            'campaign_id',
            'campaign_name',
            'adset_id',
            'adset_name',
            'reach',
            'impressions',
            'frequency',
            'spend',
            'clicks',
            'cpp',
            'cpm',
            'actions',
        ]
        params = {
            'level': 'adset',
            # 'action_attribution_windows': ['1d_click', '1d_view'],
            # 'filtering': [{'field':'delivery_info','operator':'IN','value':['active','limited']}],
            # 'filtering': [{'field':'campaign.id', 'operator':'IN', 'value':['23842968840790345']}],
            # 'breakdowns': ['age'],
            'time_range': {'since': start_date, 'until': end_date},
        }
        sort_values = ['campaign_name', 'adset_name']
    else:
        fields = [
            'campaign_id',
            'campaign_name',
            'reach',
            'impressions',
            'frequency',
            'spend',
            'clicks',
            'cpp',
            'cpm',
            'actions',
        ]
        params = {
            'level': 'campaign',
            # 'action_attribution_windows': ['1d_click', '1d_view'],
            # 'filtering': [{'field':'delivery_info','operator':'IN','value':['active','limited']}],
            # 'filtering': [{'field':'campaign.id', 'operator':'IN', 'value':['23842968840790345']}],
            # 'breakdowns': ['age'],
            'time_range': {'since': start_date, 'until': end_date},
        }
        sort_values = ['campaign_name']
    insights = AdAccount(_ad_account).get_insights(
        fields=fields,
        params=params,
    )

    df = []
    for insight in insights:
        atc = None
        lc = None
        lpv = None
        p = None
        com = None
        r = None
        sh = None
        vv = None
        for action in insight['actions']:
            if action['action_type'] == 'link_click':
                lc = action['value']
            if action['action_type'] == 'landing_page_view':
                lpv = action['value']
            if action['action_type'] == 'offsite_conversion.fb_pixel_add_to_cart':
                atc = action['value']
            if action['action_type'] == 'offsite_conversion.fb_pixel_purchase':
                p = action['value']
            if action['action_type'] == 'comment':
                com = action['value']
            if action['action_type'] == 'post_reaction':
                r = action['value']
            if action['action_type'] == 'post':
                sh = action['value']
            if action['action_type'] == 'video_view':
                vv = action['value']
        data_dict = {
            'campaign_name': insight['campaign_name'],
            'campaign_id': insight['campaign_id'],
            'adset_name': insight['adset_name'],
            'adset_id': insight['adset_id'],
            'ad_name': insight['ad_name'],
            'ad_id': insight['ad_id'],
            'spend': insight['spend'],
            'impressions': insight['impressions'],
            'link_clicks': lc,
            'clicks_all': insight['clicks'],
            'lpv': lpv,
            'atc': atc,
            'purchases': p,
            'comments': com,
            'reactions': r,
            'shares': sh,
            'video_views': vv
        }
        df.append(data_dict)
    results = pd.DataFrame(df, columns=['campaign_name',
                                        'campaign_id',
                                        'adset_name',
                                        'adset_id',
                                        'ad_name',
                                        'ad_id',
                                        'spend',
                                        'impressions',
                                        'link_clicks',
                                        'clicks_all',
                                        'lpv',
                                        'atc',
                                        'purchases',
                                        'comments',
                                        'reactions',
                                        'shares',
                                        'video_views'])
    # pd.concat(results).sort_values(sort_values)
    if _campaign_id is not None:
        df_filtered = results[results['campaign_id'] == _campaign_id]
        return df_filtered
    else:
        return results




def create_campaign(_name, _spend_cap=None, _objective='CONVERSIONS', _buying_type='AUCTION', _status='Paused', _ad_account= ad_account_id):
    from facebook_business.adobjects.campaign import Campaign
    if _spend_cap > 999:
        pr = input("Campaign spend cap is set to $" + str(_spend_cap) + " (y/n)?")
        if pr != "y":
            _spend_cap = input("Enter the correct spend cap in dollars: $")
    if _spend_cap is None:
        _spend_cap = 922337203685478 #10000 = $100
    else:
        _spend_cap = _spend_cap * 100
    print(_spend_cap)
    campaign = Campaign(parent_id=_ad_account)
    campaign.update({
        Campaign.Field.name: _name,
        Campaign.Field.objective: _objective, #APP_INSTALLS, BRAND_AWARENESS, CONVERSIONS, EVENT_RESPONSES, LEAD_GENERATION, LINK_CLICKS, LOCAL_AWARENESS, MESSAGES, OFFER_CLAIMS, PAGE_LIKES, POST_ENGAGEMENT, PRODUCT_CATALOG_SALES, REACH, VIDEO_VIEWS
        Campaign.Field.spend_cap: _spend_cap, #value of 922337203685478 will undo spend cap
        Campaign.Field.buying_type: _buying_type
    })
    if _status == 'Active':
        campaign.remote_create(params={ #remote_update to change and remote_delete to delete
            'status': Campaign.Status.active,
        })
    else:
        campaign.remote_create(params={  # remote_update to change and remote_delete to delete
            'status': Campaign.Status.paused,
        })
    return campaign


def create_adset(_name, _campaign, _optimization_goal = 'LINK_CLICKS', _billing_event = 'LINK_CLICKS', _ad_account= ad_account_id):
    from facebook_business.adobjects.adset import AdSet
    ad_account = AdAccount(fbid=_ad_account)
    params = {
        AdSet.Field.name: _name,
        AdSet.Field.optimization_goal: _optimization_goal, #AdSet.OptimizationGoal.offsite_conversions, #.post_engagement, reach enum {NONE, APP_INSTALLS, BRAND_AWARENESS, AD_RECALL_LIFT, CLICKS, ENGAGED_USERS, EVENT_RESPONSES, IMPRESSIONS, LEAD_GENERATION, LINK_CLICKS, OFFER_CLAIMS, OFFSITE_CONVERSIONS, PAGE_ENGAGEMENT, PAGE_LIKES, POST_ENGAGEMENT, REACH, SOCIAL_IMPRESSIONS, VIDEO_VIEWS, APP_DOWNLOADS, LANDING_PAGE_VIEWS, VALUE, REPLIES}
        AdSet.Field.billing_event: _billing_event, #.post_engagement, impressions
        # AdSet.Field.promoted_object: {#'page_id': c.rw_page_id,
        #                               'pixel_id': c.rw_pixel_id,
        #                               'custom_event_type': 'ADD_TO_CART' #PURCHASE, ADD_TO_CART, CONTENT_VIEW
        #                               },
        # AdSet.Field.start_time: _start_time,
        # AdSet.Field.end_time: _end_time,
        # AdSet.Field.bid_amount: 150,
        #AdSet.Field.is_autobid: True,
        AdSet.Field.bid_strategy: 'LOWEST_COST_WITHOUT_CAP',
        AdSet.Field.daily_budget: 5000,
        # AdSet.Field.lifetime_spend_cap: 50000,
        AdSet.Field.campaign_id: _campaign,
        #AdSet.Field.frequency_control_specs: [{"event": "IMPRESSIONS", "interval_days":3, "max_frequency":1}],
        AdSet.Field.targeting: {
            'geo_locations': {
                'countries': ['US']
            },
            "excluded_geo_locations": {
                "regions": [
                    {"key": "3844",
                    "name": "Alaska",
                    "country": "US"},
                    {"key": "3854",
                    "name": "Hawaii",
                    "country": "US"},
                    {"key": "3869",
                    "name": "Montana",
                    "country": "US"},
                    {"key": "3870",
                    "name": "Nebraska",
                    "country": "US"},
                    {"key": "3871",
                    "name": "Nevada",
                    "country": "US"},
                    {"key": "3874",
                    "name": "New Mexico",
                    "country": "US"},
                    {"key": "3877",
                    "name": "North Dakota",
                    "country": "US"},
                    {"key": "3884",
                    "name": "South Dakota",
                    "country": "US"},
                    {"key": "3893",
                    "name": "Wyoming",
                    "country": "US"}
                    ],
            },
            "flexible_spec":
            [
                {"interests": [
                    {"id": "1089448267745618",
                    "name": "Joanna Gaines"},
                    {"id": "1507682269559205",
                    "name": "The Holderness Family"},
                    {"id": "6002839660079",
                    "name": "Cosmetics"},
                    {"id": "6002991239659",
                    "name": "Motherhood"},
                    {"id": "6003134986700",
                    "name": "Baking"},
                    {"id": "6003161577378",
                    "name": "Groupon"},
                    {"id": "6003232518610",
                    "name": "Parenting"},
                    {"id": "6003271034848",
                    "name": "Working Mother"},
                    {"id": "6003332406177",
                    "name": "Organization"},
                    {"id": "6003372919544",
                    "name": "The Pioneer Woman - Ree Drummond"},
                    {"id": "6003385609165",
                    "name": "Recipes"},
                    {"id": "6003470511564",
                    "name": "Do it yourself (DIY)"},
                    {"id": "6003476182657",
                    "name": "Family"},
                    {"id": "6003664179678",
                    "name": "LivingSocial"},
                    {"id": "6009268249149",
                    "name": "RetailMeNot"}
                    ],
                "behaviors": [
                    {"id": "6017521096783",
                    "name": "Gmail users"}
                    ]
                }
            ],
            'age_min':28,
            'age_max': 65,
            'publisher_platforms': ['facebook', 'instagram'],  # 'audience_network', 'messenger'
            'excluded_custom_audiences': ['23842970865070345'],
            'custom_audiences': ['23842968835770345','23842968837020345'],
            'user_os':['Android_ver_4.0_and_above'],
            'excluded_user_device':['iPhone','iPad', 'iPod'],
            # 'wireless_carrier':['Wifi'],
            # 'page_types': ['desktopfeed'],
            'facebook_positions': ['feed'], #right_hand_column, instant_article, instream_video, suggested_video, marketplace
            'instagram_positions': ['stream'], #story
            'excluded_publisher_categories': ['debated_social_issues','mature_audiences','tragedy_and_conflict'],
            # 'device_platforms': ['mobile', 'desktop'],
        },
        AdSet.Field.status: AdSet.Status.active, ###Change to active

    }
    adset = ad_account.create_ad_set(params=params)
    return adset


def create_adcreative(_img=None, _name=None, _message=None, _link='https://relaygo.com/relay', _link_title=None, _link_desc=None, _keyvalue=None, _page_id = page_id, _instagram_id = instagram_id, _ad_account=ad_account_id):
    from facebook_business.adobjects.adimage import AdImage
    from facebook_business.adobjects.adcreative import AdCreative
    from facebook_business.adobjects.adcreativelinkdata import AdCreativeLinkData
    from facebook_business.adobjects.adcreativeobjectstoryspec import AdCreativeObjectStorySpec
    if _img is None:
        _img = '/Users/smalone/Desktop/Images/RelayAd_1a.png'
    if _name is None:
        _name = 'API Test AdCreative Name - DELETE'
    if _message is None:
        _message = 'Programmatic API Message'
    if _link_title is None:
        _link_title = "Relay is really awesome"
    if _link_desc is None:
        _link_desc = 'You should buy it'
    image = AdImage(parent_id=_ad_account)
    image[AdImage.Field.filename] = _img
    image.remote_create()
    image_hash = image[AdImage.Field.hash]

    link_data = AdCreativeLinkData()
    link_data[AdCreativeLinkData.Field.message] = _message
    link_data[AdCreativeLinkData.Field.link] = _link
    link_data[AdCreativeLinkData.Field.image_hash] = image_hash
    # link_data[AdCreativeLinkData.Field.format_option] = 'single_image' #carousel_images_multi_items, carousel_images_single_item, carousel_slideshows
    link_data[AdCreativeLinkData.Field.name] = _link_title
    link_data[AdCreativeLinkData.Field.caption] = 'relaygo.com'
    link_data[AdCreativeLinkData.Field.description] = _link_desc
    link_data[AdCreativeLinkData.Field.call_to_action] = {"type":"LEARN_MORE",
                                                          "value": {"link":_link,}}

    object_story_spec = AdCreativeObjectStorySpec()
    object_story_spec[AdCreativeObjectStorySpec.Field.page_id] = _page_id
    object_story_spec[AdCreativeObjectStorySpec.Field.instagram_actor_id] = _instagram_id
    object_story_spec[AdCreativeObjectStorySpec.Field.link_data] = link_data

    creative = AdCreative(parent_id=_ad_account)
    creative[AdCreative.Field.name] = _name
    creative[AdCreative.Field.object_story_spec] = object_story_spec
    if _keyvalue != None:
        creative[AdCreative.Field.url_tags] = _keyvalue
    creative.remote_create()

    return creative




def create_ad(_creative, _adset_id=None, _name=None, _status='Active', _ad_account=ad_account_id):
    from facebook_business.adobjects.ad import Ad
    if _name is None:
        _name='API Test Ad Name - DELETE'
    ad = Ad(parent_id=_ad_account)
    ad[Ad.Field.name] = _name
    ad[Ad.Field.adset_id] = _adset_id
    ad[Ad.Field.tracking_specs] = [
                    {
                    "action.type": ["offsite_conversion"],
                    "fb_pixel": ["153097368750576"]
                    },
                ]
    if is_number(_creative):
        ad[Ad.Field.creative] = {
            'creative_id': _creative,
        }
    else:
        ad[Ad.Field.creative] = _creative

    if _status == 'Active':
        ad.remote_create(params={
            'status': Ad.Status.active,
        })
    else:
        ad.remote_create(params={
            'status': Ad.Status.paused,
        })
    return ad

