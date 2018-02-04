from map import *


def create_map(players, map_name, board_id):
    """
    Creates map of type World
    :param players: dict
    :param map_name: string
    :param board_id: int
    :return: Board
    """
    alaska = Territory('alaska', 'Alaska')
    northwestTer = Territory('northwestTer', 'Northwest Territory')
    greenland = Territory('greenland', 'Greenland')
    alberta = Territory('alberta', 'Alberta')
    ontario = Territory('ontario', 'Ontario')
    quebec = Territory('quebec', 'Quebec')
    westUS = Territory('westUS', 'Western United States')
    eastUS = Territory('eastUS', 'Eastern United States')
    centralAmer = Territory('centralAmer', 'Central America')
    venezuela = Territory('venezuela', 'Venezuela')
    peru = Territory('peru', 'Peru')
    brazil = Territory('brazil', 'Brazil')
    argentina = Territory('argentina', 'Argentina')
    iceland = Territory('iceland', 'Iceland')
    scandinavia = Territory('scandinavia', 'Scandinavia')
    ukraine = Territory('ukraine', 'Ukraine')
    greatBritain = Territory('greatBritain', 'Great Britain')
    northEur = Territory('northEur', 'Northern Europe')
    westEur = Territory('westEur', 'Western Europe')
    southEur = Territory('southEur', 'Southern Europe')
    ural = Territory('ural', 'Ural')
    siberia = Territory('siberia', 'Siberia')
    yakutsk = Territory('yakutsk', 'Yakutsk')
    kamchatka = Territory('kamchatka', 'Kamchatka')
    irkutsk = Territory('irkutsk', 'Irkutsk')
    mongolia = Territory('mongolia', 'Mongolia')
    japan = Territory('japan', 'Japan')
    afghanistan = Territory('afghanistan', 'Afghanistan')
    china = Territory('china', 'China')
    middleEast = Territory('middleEast', 'Middle East')
    india = Territory('india', 'India')
    siam = Territory('siam', 'Siam')
    northAfr = Territory('northAfr', 'Northern Africa')
    egypt = Territory('egypt', 'Egypt')
    eastAfr = Territory('eastAfr', 'Eastern Afr')
    congo = Territory('congo', 'Congo')
    madagascar = Territory('madagascar', 'Madagascar')
    southAfr = Territory('southAfr', 'Southern Africa')
    indonesia = Territory('indonesia', 'Indonesia')
    newGuinea = Territory('newGuinea', 'New Guinea')
    westAustr = Territory('westAustr', 'Western Australia')
    eastAustr = Territory('eastAustr', 'Eastern Australia')

    set_connections(
        (alaska, northwestTer),
        (alaska, kamchatka),
        (alaska, alberta),
        (northwestTer, alberta),
        (northwestTer, ontario),
        (northwestTer, greenland),
        (alberta, ontario),
        (alberta, westUS),
        (ontario, westUS),
        (ontario, eastUS),
        (ontario, greenland),
        (ontario, quebec),
        (quebec, greenland),
        (quebec, eastUS),
        (westUS, eastUS),
        (westUS, centralAmer),
        (eastUS, centralAmer),
        (centralAmer, venezuela),
        (greenland, iceland),
        (venezuela, brazil),
        (venezuela, peru),
        (peru,  brazil),
        (peru, argentina),
        (brazil, argentina),
        (brazil, northAfr),
        (northAfr, egypt),
        (northAfr, eastAfr),
        (northAfr, congo),
        (northAfr, westEur),
        (northAfr, southEur),
        (egypt, eastAfr),
        (egypt, middleEast),
        (egypt, southEur),
        (eastAfr, congo),
        (eastAfr, southAfr),
        (eastAfr, madagascar),
        (congo, southAfr),
        (southAfr, madagascar),
        (iceland, greatBritain),
        (iceland, scandinavia),
        (greatBritain, westEur),
        (greatBritain,  northEur),
        (greatBritain, scandinavia),
        (ukraine, scandinavia),
        (northEur, scandinavia),
        (northEur, southEur),
        (westEur, northEur),
        (westEur, southEur),
        (northEur, ukraine),
        (southEur, ukraine),
        (southEur, middleEast),
        (ukraine, middleEast),
        (ukraine, afghanistan),
        (ukraine, ural),
        (middleEast, afghanistan),
        (middleEast, india),
        (afghanistan, ural),
        (afghanistan, china),
        (afghanistan, india),
        (ural, siberia),
        (ural, china),
        (siberia, yakutsk),
        (siberia, irkutsk),
        (siberia, mongolia),
        (siberia, china),
        (china, mongolia),
        (china, india),
        (china, siam),
        (india, siam),
        (siam, indonesia),
        (mongolia, irkutsk),
        (mongolia, kamchatka),
        (mongolia,  japan),
        (japan, kamchatka),
        (irkutsk, yakutsk),
        (irkutsk, kamchatka),
        (yakutsk, kamchatka),
        (indonesia, newGuinea),
        (indonesia, westAustr),
        (newGuinea, westAustr),
        (newGuinea, eastAustr),
        (westAustr, eastAustr)
    )

    unitchart = {2: 50, 3: 35, 4: 30, 5: 25, 6: 20}

    northAmerica = Continent('NorthAmerica', [alaska, northwestTer, greenland, alberta, ontario, quebec, westUS,
                                       eastUS, centralAmer], 5)
    southAmerica = Continent('SouthAmerica', [venezuela, peru, brazil, argentina], 2)
    europe = Continent('Europe', [iceland, scandinavia, ukraine, greatBritain, northEur, westEur, southEur], 5)
    asia = Continent('Asia', [ural, siberia, yakutsk, kamchatka, irkutsk, mongolia, japan, afghanistan, china,
                              middleEast, india, siam], 7)
    africa = Continent('Africa', [northAfr, egypt, eastAfr, congo, madagascar, southAfr], 3)
    australia = Continent('Australia', [indonesia, newGuinea, westAustr, eastAustr], 2)

    board = Board(board_id, {'alaska': alaska, 'northwestTer': northwestTer, 'greenland': greenland, 'alberta': alberta,
                   'ontario': ontario, 'quebec': quebec, 'westUS': westUS, 'eastUS': eastUS, 'centralAmer': centralAmer,
                   'venezuela': venezuela, 'peru': peru, 'brazil': brazil, 'argentina': argentina, 'iceland': iceland,
                   'scandinavia': scandinavia, 'ukraine': ukraine, 'greatBritain': greatBritain, 'northEur': northEur,
                   'westEur': westEur, 'southEur': southEur, 'ural': ural, 'siberia': siberia, 'yakutsk': yakutsk,
                   'kamchatka': kamchatka, 'irkutsk': irkutsk, 'mongolia': mongolia, 'japan': japan,
                   'afghanistan': afghanistan, 'china': china, 'middleEast': middleEast, 'india': india, 'siam': siam,
                   'northAfr': northAfr, 'egypt': egypt, 'eastAfr': eastAfr, 'congo': congo, 'madagascar': madagascar,
                   'southAfr': southAfr, 'indonesia': indonesia, 'newGuinea': newGuinea, 'westAustr': westAustr,
                   'eastAustr': eastAustr},
                  {'northAmerica': northAmerica, 'southAmerica': southAmerica, 'europe': europe, 'asia': asia,
                   'africa': africa, 'australia': australia},
                  players, map_name, unitchart)

    return board
