

def band_info(band):
    text = f'<b>{band.name.upper()}</b>'
    text += f'\n\n{band.tag_name}'

    if band.genre and band.genre != band.tag_name:
        text += f'\n{band.genre}'

    text += f'\n\n{band.description}'
    return text


def venue_info(venue):
    text = f'<b>{venue.name.upper()}</b>'
    text += f'\n\n{venue.address}'

    if venue.description:
        text += f'\n\n{venue.description}'

    return text


def event_info(event):
    text = f'<b><a href="%s">%s</a></b>' % (event.link, event.title)
    for band in event.bands:
        text += '\n🎸 %s' % f'{band.name} ({band.tag_name})'
    text += '\n📅 %s: ' % event.get_date_human_format()
    text += '\n🕑 %s' % event.get_time_human_format()
    text += '\n📍 %s' % event.get_place()
    if not event.price:
        text += '\n💰 Gratuito'
    else:
        text += '\n💰 %.2f€' % event.price
        if event.price_preorder and event.price_preorder != event.price:
            text += ' (Anticipada: %.2f€)' % event.price_preorder

    return text


def news_list_info(news_list):
    separator = "\n\n〰〰〰〰〰〰〰〰〰\n\n"
    text = separator
    for news in news_list:
        text += '🗞 <b><a href="%s">%s</a></b>' % (news.get_web_link(), news.title)
        text += f'\n🗓 <i>{news.get_publication_date_human()}</i>'
        text += f'\n{news.subtitle}{separator}'
    return text

