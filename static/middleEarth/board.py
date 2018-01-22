from map import *


def create_map(players, map_name):
    lindon = Territory('lindon', 'Lindon')
    eriador = Territory('eriador', 'Eriador')
    forodwaith = Territory('forodwaith', 'Forodwaith')
    enedwaith = Territory('enedwaith', 'Enedwaith')
    moria = Territory('moria', 'Moria')
    rhovanion = Territory('rhovanion', 'Rhovanion')
    rohan = Territory('rohan', 'Rohan')
    gondor = Territory('gondor', 'Gondor')
    rhun = Territory('rhun', 'Rhun')
    mordor = Territory('mordor', 'Mordor')
    khand = Territory('khand', 'Khand')
    harad = Territory('harad', 'Harad')

    set_connections(
        (lindon, eriador),
        (lindon, forodwaith),
        (eriador, forodwaith),
        (eriador, enedwaith),
        (enedwaith, moria),
        (forodwaith, rhovanion),
        (moria, rhovanion),
        (moria, rohan),
        (rohan, gondor),
        (rohan, rhun),
        (rhovanion, rhun),
        (gondor, mordor),
        (rhun, mordor),
        (rhun, khand),
        (mordor, khand),
        (rohan, mordor),
        (mordor, harad),
        (khand, harad),
        (gondor, harad)
    )

    unitchart = {2: 15, 3: 12, 4: 9, 5: 7, 6: 6}

    arnor = Continent('Arnor', [lindon, eriador, enedwaith], 2)
    shadowlands = Continent('Shadowlands', [mordor, rhun, khand], 1)

    board = Board({'lindon': lindon, 'eriador': eriador, 'forodwaith': forodwaith, 'enedwaith': enedwaith,
                   'moria': moria, 'rhovanion': rhovanion, 'rohan': rohan, 'gondor': gondor, 'rhun': rhun,
                   'mordor': mordor, 'khand': khand, 'harad': harad},
                  {'arnor': arnor, 'shadowlands': shadowlands},
                  players, map_name, unitchart)

    return board
