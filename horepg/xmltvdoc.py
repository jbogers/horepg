import xml.dom.minidom
import time
import logging


def debug(msg):
  logging.debug(msg)


def warning(msg):
  logging.warning(msg)


class XMLTVDocument(object):
  # this renames some of the channels
  add_display_name = {}
  # Target names taken from: https://github.com/tvheadend/tvheadend/blob/master/src/epg.c
  # All entries must be lower case
  category_map = {
    # 00
    'onbepaald': '',
    'miniseries': '',  # Format, not content
    'event': '',  # Used for various categories

    # 01
    'tv drama': 'movie/drama',
    'actie': 'movie/drama',
    'familie': 'movie/drama',
    'dramaseries': 'movie/drama',
    'thriller': 'detective/thriller',
    'detective': 'detective/thriller',
    'mysterie': 'detective/thriller',
    'misdaaddrama': 'detective/thriller',
    'avontuur': 'adventure/western/war',
    'western': 'adventure/western/war',
    'horror': 'science fiction/fantasy/horror',
    'sci-fi': 'science fiction/fantasy/horror',
    'sci-fi/horror': 'science fiction/fantasy/horror',
    'sciencefiction': 'science fiction/fantasy/horror',
    'fantasy': 'science fiction/fantasy/horror',
    'komedie': 'comedy',
    'sitcoms': 'comedy',
    'zwarte komedie': 'comedy',
    'standup komedie': 'comedy',
    'melodrama': 'soap/melodrama/folkloric',
    'soap': 'soap/melodrama/folkloric',
    'romantiek': 'romance',
    'romantisch': 'romance',
    'romantische komedie': 'romance',
    'drama': 'serious/classical/religious/historical movie/drama',
    'historisch drama': 'serious/classical/religious/historical movie/drama',
    'erotiek': 'adult movie/drama',
    'erotisch': 'adult movie/drama',

    # 02
    'nieuws': 'news/current affairs',
    'actualiteit': 'news/current affairs',
    'actualiteitenprogramma\'s': 'news/current affairs',
    'weer': 'news/weather report',
    'nieuws documentaire': 'news magazine',
    'documentaire': 'documentary',
    'historisch': 'documentary',
    'geschiedenis': 'documentary',
    'waar gebeurd': 'documentary',
    'docudrama': 'documentary',
    'docusoap': 'documentary',
    'discussie': 'discussion/interview/debate',
    'interview': 'discussion/interview/debate',
    'debat': 'discussion/interview/debate',

    # 03
    'show': 'show/game show',
    'entertainment': 'show/game show',
    'spelshow': 'show/game show',
    'variété': 'variety show',
    'variete': 'variety show',
    'theater': 'variety show',
    'bloemlezing': 'variety show',
    'talkshow': 'talk show',
    'talk show': 'talk show',

    # 04
    'sport': 'sports',
    'extreme sporten': 'sports',
    'snooker': 'sports',
    'tennis': 'sports',
    'golf': 'sports',
    'snowboarden': 'sports',
    'skiën': 'sports',
    'freestyle skiën': 'sports',
    'alpineskiën': 'sports',
    'skispringen': 'sports',
    'vliegsport': 'sports',
    'triathlon': 'sports',
    'biathlon': 'sports',
    'schermen': 'sports',
    'kunstschaatsen': 'sports',
    'gewichtheffen': 'sports',
    'boksen': 'sports',
    'stierenvechten': 'sports',
    'gamen': 'sports',
    'evenementen': 'special events (olympic games, world cup, etc.)',
    'olympische spelen': 'special events (olympic games, world cup, etc.)',
    'sportmagazine': 'sports magazines',
    'sporttalkshow': 'sports magazines',
    'voetbal': 'football/soccer',
    'american football': 'football/soccer',
    'tennis/squash': 'tennis/squash',
    'teamsporten': 'team sports (excluding football)',
    'hockey': 'team sports (excluding football)',
    'basketbal': 'team sports (excluding football)',
    'wielrennen': 'team sports (excluding football)',
    'atletiek': 'athletics',
    'turnen': 'athletics',
    'motorsport': 'motor sport',
    'extreme': 'motor sport',
    'motors': 'motor sport',
    'motorracen': 'motor sport',
    'watersport': 'water sport',
    'wintersport': 'winter sports',
    'paardensport': 'equestrian',
    'gevechtssport': 'martial sports',
    'worstelen': 'martial sports',
    'mixed martial arts (mma)': 'martial sports',

    # 05
    'kids/jeugd': 'children\'s / youth programs',
    'kinderen': 'children\'s / youth programs',
    'kids 0 - 6': 'pre-school children\'s programs',
    'kids, 0-6': 'pre-school children\'s programs',
    'jeugd 6 - 14': 'entertainment programs for 6 to 14',
    'jeugd 10 - 16': 'entertainment programs for 10 to 16',
    'educatie': 'information/educational/school program',
    'poppenspel': 'cartoon/puppets',
    'animatie': 'cartoon/puppets',
    'anime': 'cartoon/puppets',

    # 06
    'muziek': 'music/ballet/dance',
    'easy listening': 'music/ballet/dance',
    'dans': 'music/ballet/dance',
    'rock/pop': 'rock/pop',
    'klassiek': 'serious music/classical music',
    'volksmuziek': 'folk/traditional music',
    'jazz': 'jazz',
    'musical': 'musical/opera',
    'musical/opera': 'musical/opera',
    'opera': 'musical/opera',
    'ballet': 'ballet',

    # 07
    'lifestyle': 'arts/culture (without music)',
    'beeldende kunst': 'performing arts',
    'podiumkunsten': 'performing arts',
    'religie': 'religion',
    'popart': 'popular culture/traditional arts',
    'literatuur': 'literature',
    'speelfilm': 'film/cinema',
    'film': 'film/cinema',
    'film/cinema': 'film/cinema',
    'shorts': 'experimental film/video',
    'special': 'broadcasting/press',
    'kunst magazine': 'arts magazines/culture magazines',
    'kunst/cultuur': 'arts magazines/culture magazines',
    'kunstnijverheid': 'arts magazines/culture magazines',
    'mode': 'fashion',

    # 08
    'maatschappelijk': 'social/political issues/economics',
    'consumentenprogramma\'s': 'social/political issues/economics',
    'reality': 'social/political issues/economics',
    'politiek': 'social/political issues/economics',
    'oorlog': 'social/political issues/economics',
    'militair': 'social/political issues/economics',
    'zelfhulp': 'social/political issues/economics',
    'veiling': 'social/political issues/economics',
    'paranormaal': 'social/political issues/economics',
    'lhbti': 'social/political issues/economics',
    'actualiteiten': 'magazines/reports/documentary',
    'cheerleading': 'magazines/reports/documentary',
    'opvoeden': 'magazines/reports/documentary',
    'economie': 'economics/social advisory',
    'business & financial': 'economics/social advisory',
    'recht': 'economics/social advisory',
    'misdaad': 'economics/social advisory',
    'beroemdheden': 'remarkable people',
    'biografie': 'remarkable people',

    # 09
    'natuur': 'nature/animals/environment',
    'natuur en milieu': 'nature/animals/environment',
    'dieren': 'nature/animals/environment',
    'technologie': 'technology/natural sciences',
    'wetenschap': 'technology/natural sciences',
    'computers': 'technology/natural sciences',
    'geneeskunde': 'medicine/physiology/psychology',
    'medisch': 'medicine/physiology/psychology',
    'expedities': 'foreign countries/expeditions',
    'sociologie': 'social/spiritual sciences',
    'samenleving': 'social/spiritual sciences',
    'educatie divers': 'further education',
    'talen': 'languages',

    # 10
    'vrije tijd': 'leisure hobbies',
    'vakantie': 'leisure hobbies',
    'outdoor': 'leisure hobbies',
    'auto\'s': 'leisure hobbies',
    'vissen': 'leisure hobbies',
    'verzamelen': 'leisure hobbies',
    'landbouw': 'leisure hobbies',
    'reizen': 'tourism / travel',
    'klussen': 'handicraft',
    'doe-het-zelf': 'handicraft',
    'bouwen en verbouwen': 'handicraft',
    'auto en motor': 'motoring',
    'gezondheid': 'fitness and health',
    'exercise': 'fitness and health',
    'fit en gezond': 'fitness and health',
    'koken': 'cooking',
    'culinair': 'cooking',
    'shoppen': 'advertisement / shopping',
    'tuinieren': 'gardening',
    'home & garden': 'gardening',
  }

  def __init__(self):
    impl = xml.dom.minidom.getDOMImplementation()
    doctype = impl.createDocumentType('tv', None, 'xmltv.dtd')
    self.document = impl.createDocument(None, 'tv', doctype)
    self.document.documentElement.setAttribute('source-info-url', 'https://horizon.tv')
    self.document.documentElement.setAttribute('source-info-name', 'UPC Horizon API')
    self.document.documentElement.setAttribute('generator-info-name', 'HorEPG v1.0')
    self.document.documentElement.setAttribute('generator-info-url', 'beralt.nl/horepg')

  def addChannel(self, channel_id, display_name, icon=None):
    element = self.document.createElement('channel')
    element.setAttribute('id', channel_id)

    if display_name in XMLTVDocument.add_display_name:
      for name in XMLTVDocument.add_display_name[display_name]:
        dn_element = self.document.createElement('display-name')
        dn_text = self.document.createTextNode(name)
        dn_element.appendChild(dn_text)
        element.appendChild(dn_element)
    else:
      if type(display_name) == list:
        for name in display_name:
          dn_element = self.document.createElement('display-name')
          dn_text = self.document.createTextNode(name)
          dn_element.appendChild(dn_text)
          element.appendChild(dn_element)
      else:
        dn_element = self.document.createElement('display-name')
        dn_text = self.document.createTextNode(display_name)
        dn_element.appendChild(dn_text)
        element.appendChild(dn_element)

    if (icon):
      lu_element = self.document.createElement('icon')
      lu_element.setAttribute('src', icon)
      element.appendChild(lu_element)

    self.document.documentElement.appendChild(element)

  def addProgramme(self, channel_id, title, start, end, episode=None, episode_title=None, description=None,
                   categories=None):
    element = self.document.createElement('programme')
    element.setAttribute('start', XMLTVDocument.convert_time(int(start)))
    element.setAttribute('stop', XMLTVDocument.convert_time(int(end)))
    element.setAttribute('channel', channel_id)
    # quick tags
    self.quick_tag(element, 'title', title)
    if episode:
      self.quick_tag(element, 'episode-num', episode, {'system': 'onscreen'})
    if description:
      self.quick_tag(element, 'desc', description)
    if episode_title:
      self.quick_tag(element, 'sub-title', episode_title)
    # categories
    if categories:
      for cat in categories:
        cat_title = XMLTVDocument.map_category(cat.lower())
        if cat_title is not None:
          self.quick_tag(element, 'category', cat_title)
        elif '/' not in cat:
          warning("CHANNEL '{}', PROGRAM '{}': No XMLTV translation for category '{}'".format(channel_id, title, cat))
          self.quick_tag(element, 'category', cat.lower())
        else:
          debug(
            "CHANNEL '{}', PROGRAM '{}': Skipping category '{}' due to '/'".format(channel_id, title, cat))
    self.document.documentElement.appendChild(element)

  def map_category(cat):
    if cat in XMLTVDocument.category_map:
      return XMLTVDocument.category_map[cat]
    return None

  def quick_tag(self, parent, tag, content, attributes=False):
    element = self.document.createElement(tag)
    text = self.document.createTextNode(content)
    element.appendChild(text)
    if attributes:
      for k, v in attributes.items():
        element.setAttribute(k, v)
    parent.appendChild(element)

  def convert_time(t):
    return time.strftime('%Y%m%d%H%M%S', time.gmtime(t))
