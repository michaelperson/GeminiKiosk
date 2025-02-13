from smartcard.scard import *
from smartcard.util import toHexString
import threading
import time

class RFIDPCSCReader:
    def __init__(self):
        self.hresult, self.hcontext = SCardEstablishContext(SCARD_SCOPE_USER)
        self.is_running = False
        self.callback = None
        self._check_pcsc_status()
        self.APDU_COMMANDS = {
        "ACS ACR1252": [0xFF, 0xCA, 0x00, 0x00, 0x00],   
        "ACS ACR1552": [0x00, 0xA4, 0x04, 0x00, 0x00],   
        }

    def find_first_matching_key(self,reader_name, commands):
        """
        Trouve la première clé du dictionnaire `commands` qui est contenue dans le `reader_name`.
        """
        print('recherche')
        value=[0x00, 0xA4, 0x04, 0x00, 0x00]
        for key in commands:
            if key in reader_name:
                value=commands[key]
        return value  # Retourne None si aucune clé correspondante n'est trouvée

    def _check_pcsc_status(self):
        """Vérifie que le service pcscd est accessible"""
        if self.hresult != SCARD_S_SUCCESS:
            raise Exception("Impossible d'établir le contexte PC/SC. Vérifiez que pcscd est en cours d'exécution.")

    def set_callback(self, callback_function):
        """Définit la fonction à appeler quand un tag RFID est lu"""
        self.callback = callback_function

    def _get_readers(self):
        """Récupère la liste des lecteurs connectés"""
        hresult, readers = SCardListReaders(self.hcontext, [])
        if hresult != SCARD_S_SUCCESS or not readers:
            raise Exception("Aucun lecteur RFID trouvé. Vérifiez la connexion et le service pcscd.")
        
        # Assure que les noms des lecteurs sont des strings
        readers = [r.decode('utf-8') if isinstance(r, bytes) else r for r in readers]
        return readers

    def _read_card(self, reader):
        """Lit une carte RFID sur le lecteur spécifié"""
        try:
            hresult, hcard, dwActiveProtocol = SCardConnect(
                self.hcontext,
                reader,
                SCARD_SHARE_SHARED,
                SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1
            )

            if hresult != SCARD_S_SUCCESS:
                return None
            reader_name = reader
            # Commande APDU pour lire l'ID de la carte
            cmd =  self.find_first_matching_key(reader_name, self.APDU_COMMANDS)
            #cmd = [0xFF, 0xCA, 0x00, 0x00, 0x00]

            try:
                hresult, response = SCardTransmit(hcard, dwActiveProtocol, cmd)
                if hresult == SCARD_S_SUCCESS:
                    card_id = toHexString(response[:-2])  # Ignore le statut (les 2 derniers octets)
                    return card_id
            finally:
                SCardDisconnect(hcard, SCARD_UNPOWER_CARD)

        except Exception as e:
            print(f"Erreur lors de la lecture de la carte: {e}")
            return None

    def _monitor_thread(self):
        """Fonction principale du thread de surveillance"""
        while self.is_running:
           # try:
                readers = self._get_readers()
                 
                for reader in readers:
                     
                    # Vérifie la présence d'une carte
                    hresult, reader_states = SCardGetStatusChange(
                        self.hcontext,
                        100,  # Timeout en ms
                        [(reader, SCARD_STATE_UNAWARE)]
                    )
                     
                    if hresult == SCARD_S_SUCCESS:
                        current_state = reader_states[0][1] 
                        if current_state & SCARD_STATE_PRESENT:
                            card_id = self._read_card(reader)
                            if card_id and self.callback:
                                self.callback(card_id)

           # except Exception as e:
           #     print(f"Erreur dans la boucle de surveillance: {e}")
           #     time.sleep(1)  # Évite une utilisation CPU excessive en cas d'erreur

    def start(self):
        """Démarre la surveillance RFID dans un thread séparé"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._monitor_thread)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """Arrête la surveillance RFID"""
        self.is_running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        SCardReleaseContext(self.hcontext)


