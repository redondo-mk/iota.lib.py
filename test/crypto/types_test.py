# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

import warnings
from unittest import TestCase

from iota import Hash, TryteString
from iota.crypto import SeedWarning
from iota.crypto.types import Digest, PrivateKey, Seed


class SeedTestCase(TestCase):
  def test_random(self):
    """
    Generating a random seed.
    """

    with warnings.catch_warnings(record=True) as catched_warnings:

      # all warnings should be triggered
      warnings.simplefilter("always")

      seed = Seed.random()

      self.assertEqual(len(catched_warnings), 0)

    # Regression test: ``random`` MUST return a :py:class:`Seed`, NOT a
    # :py:class:`TryteString`!
    self.assertIsInstance(seed, Seed)

    # Regression test: Random seed must be exactly 81 trytes long.
    # https://github.com/iotaledger/iota.lib.py/issues/44
    self.assertEqual(len(seed), Hash.LEN)

  def test_random_seed_too_long(self):
    """
    Generating a random seed, which is too long.
    """

    with warnings.catch_warnings(record=True) as catched_warnings:

      # Cause seed related warnings to be triggered
      warnings.simplefilter("always", category=SeedWarning)

      seed = Seed.random(length=Hash.LEN + 1)

      # check attributes of warning
      self.assertEqual(len(catched_warnings), 1)
      self.assertIs(catched_warnings[-1].category, SeedWarning)
      self.assertIn("inappropriate length", str(catched_warnings[-1].message))

      self.assertEqual(len(seed), Hash.LEN + 1)


class DigestTestCase(TestCase):
  def test_init_error_too_long(self):
    """
    A digest's length must be a multiple of :py:attr:`Hash.LEN` trytes.
    """
    with self.assertRaises(ValueError):
      Digest(b'9' * (Hash.LEN + 1))

    with self.assertRaises(ValueError):
      Digest(b'9' * (2 * Hash.LEN + 1))

  def test_init_error_too_short(self):
    """
    A digest's length must be a multiple of :py:attr:`Hash.LEN` trytes.
    """
    with self.assertRaises(ValueError):
      Digest(b'9' * (Hash.LEN - 1))

    with self.assertRaises(ValueError):
      Digest(b'9' * (2 * Hash.LEN - 1))


# noinspection SpellCheckingInspection
class PrivateKeyTestCase(TestCase):
  """
  Generating validation data using the JS lib:

  .. code-block:: javascript

     // Specify parameters used to generate the private key.
     var seed = 'SEED9GOES9HERE';
     var keyIndex = 42;
     var securityLevel = 3;

     var Converter = require('./lib/crypto/converter/converter');
     var Signing = require('./lib/crypto/signing/signing');

     // Generate the key and corresponding digest.
     var privateKey = Signing.key(Converter.trits(seed), keyIndex, securityLevel);
     var digest = Signing.digests(privateKey);

     // Output human-readable version of the digest.
     console.log(Converter.trytes(digest));

  References:
    - ``lib/api/api.js:api.prototype._newAddress``
  """
  def test_get_digest_single_fragment(self):
    """
    Generating digest from a PrivateKey 1 fragment long.
    """
    key =\
      PrivateKey(
        b'YYKM9AOPBSOSKZJRE9LIUNGFEBPWAK9JQD9LNKVLLOBVYTDQ9QMRNWJHWGTBFLCCYPQ9B9YMJMORDVGDCCVYAQOYFVGZKYUKXTLLUVWNRKIBYZEQFLYRWYRZNWKJAGVWO9VDRSYCAOARINNIL9EQKBREAGEZMBIXSZKVWRRNRLUYAYYUZUYHW9DUJJKJQVMJCPZFBLAURYJGZLT9ZHBLNUQWE9YVJFMWWZNJRHFSPVCQKJMWUCYPYUBHA9QEPCFAYWMGQOFDLZXDQSPYSSDL9MKJAPUGQWGAIRJC9MEYNTMABQTKVIHLSYSNSWAZGJL9YLIZWIO9G9LNRNENQHVZK9YXNQTJSFIJQPLVWWCJ9UTEEYGVFJVUVBJPHKBZACPVQFQCQAVDV9BUTXLFQSHIXZTEONSVKECHCVICRRUZGIPGEFMGUK9QQOPKMYHTDPIIKKDELF9DGSBBEHESJETZSPYTXSAPYA9ZSRKHECXXT9TTKSRIMRFKBBHFKQIYIJGJNSTZRGORHZLVEVLGGXTUHBEDGFIEVFZBQDCNJPQQ9DXMPP9KJD9PBZWKUT9ZPYW9FHBSSNSVTTGHSEVIHYFSUCIRDXSHWCOOGPTTJCCFNHYLRQHRQOBVNUNROWRSYQATJCSSYUGZ9YWFNJHIQNZMIGYKPDFR9JXMAJHQIR9PEWZRHYMOVJNQUXHKNRZEIJMQOZIQVOUSNEQRCYEIAVMHHUA9XIG9CQSBYCDQGEHHZPGSQCHY9OIBBSHSGTORMXIUAXERVPBZ9OGHBCDRXOUFNFJDKALLQOQFMWHHIPJSOAQTHUUFJWCTCROCFSYLOBHIYWCFJQHGWSGGKJRSKZGNUBDMGQZZM9SEZQXABXYFROYUYOHJEPPGCLCWOTZZGYVTBZH9AWPCVGILCDUWRQVLPDEJLVUKNNKBFFXSMVTAIZGBBJMMOAHGLMASBICFUQKWAKHEVNDQPNHDXSJFYGQOVWOKTWDSRGWCWNF9KP9VFOCTED9LIDRIPBLBMWUGRUIPENOFHSATAKHBRHQFDDEOZOZSDZKZWYNWDXVEMRASWCVMFNESLVUIFQNXXDABDGBBUICOZRAADRKQHRYRD9PVTWAETJCAOQIRNZGSULUWMZIVQZR9WDZVBAQXWBFPQRINPKDHGIMWMEOHOKODFSO9DSEZOPAWFLIYBUZWP9OYSTWFNKEFWYGPUTEZOGDKMZCQOYNTEONUSNSBNBMMPFGFTCUID9AELBVGZHYTJ9VSUQLFZDYYOCBMFYHFNFPOLUHGTLFXRWD9JUHFTU9DMSALSARRPYVHDEQTGY9TYTRUHD9YWCZFUTNNJPPRSZPPARMVKWVRMFIEGVJYXEMQTCDGZPAFHNIJTNPZYVGT9RQWKBZZ9CKRKAFMKGDKXGJUZHMDNWUPZYLDDVSORPMCCDLPGIIIYAVDLJODEVRPQIA9JLSEYQTIGDTNGYRNVIQBFBFLYVHDUORTCFFIWOBQJXQ9NUXAHI9TUVR9SJKTST9MGJIIBGDIFRELOHDW9MXPARDLG9WQWLIC9TTHVOSQ9FCAFDCSUHHISCWVJNYWHKVMPYBKVORHRGVY9PDHXPNDXIMJMYECYQZGDT9DANTQBJPXHN9MG9MDKJ9EJIDQZFLJX9VPACAHZUXMBMPRUGNHBXFCGBDYUWAIPFVAMQZYMLESKEEIKFWQVPJRBQBCDOYVSUFTONAIHMIUEVPXTWUYADPQLMBLKWCYXETFVLTZZATEHYDTHSDXAJMQDLKYNQNUAZBVYRLCVKAOUWA9QHXK9AXYFZGBUAZLVZGLVRKSHVRLXTYKMPDCZURJOSTHVJFCKIXHXXQQNCBTAEXUVMKMKEQVUPOEEY9LSTKT9XNJVJPRK9ZDUFQWTMJHWNMTTDRCRMFRXUEZMYXLQEAQMEV9MBIORUONCARJVMCDIR9PIOUJUXIDFY9NHCENUCVPJDIKHIRVRFPGKDZSIGZSBZGTRWAXLRFQLESYXKUISYBTWGZPAVNIKVXLYGINAUMZSJAMDRM9LVAXXCBSOBXUAKFAPMVAXDPFZTKWQCEOKBKAJWELYR9ZEWOTTNFOLHCNUPNMJO9CBH9HXTKFCSXMGBVHY9QFLDFNYMGQUEOXMEPBZWTOKHUMFIJKLUMYPZJHNKIBTRCDSNRBFOSPMDMYCRTBQJZZASRRNIOZTAZ',
      )

    self.assertEqual(
      key.get_digest(),

      TryteString(
        b'TIBCVWNGKLYX9UDSNQK9FWFODLGWOZREMZYWYRPILH9LYLOSRJSZQKKXBBEGVRJYTFHWQXRAMPMRJJT99',
      ),
    )

  def test_get_digest_multiple_fragments(self):
    """
    Generating digest from a PrivateKey longer than 1 fragment.
    """
    key =\
      PrivateKey(
        # This key is 3 fragments long (split into separate lines to
        # improve IDE performance).
        b'KDCFNMNMIFDAX9ACOQMUKGHSXEFHDPHBXBKVCGNENDGZGUAFVZGLPPUASMOWVOYUT9BNGXJ9HHLXHFBGWQCNXMCDXMYTVNWRCDLTCAOORGEPRGHYGHUPVEGCOILRPXMOTMDLYVYSUXTBRZDERVNBLFSVPLXQIHPCP9CRKHPJDIWXTEDZTODIKJBVC9LOO9NZLUDNPKPXUZJXNWQRYCKYYGDAGDTSVBN9LDLHJFVEAZYYYJHUVHDIDNOUHKXOTPZAXIRX999YGKIBZFCKEOGA9HVRSTPQPBS9GS9THHILCTUATKQVKOJHOT9OAVKRBPIROLSZADVRGWKH9MSYWIXEYECSIZJCJDSESQTTW9EADQTOUWAXOXXZGYFBGSPIJLTEUOZFYMFODMIWFFYMPIJN9QZNYSSRGELQJAWPHXKIFFEVDIGYUSXMALQNJCCP9SJCOFWHTVVDLPWDEYDY9UIGRJYEANTXZXJGVGGMLXYTPQMELTXXDHKGZSODPGGXKQQYX9HSWSRLUJENERYZJLCEEAMDADYAAYAOAYEROJQPWAJWIHRZQWXFRXDYZP9AHFVGFBJWGZOUFFWECNLXVIDMCRTKGCMWL9RMMEPSFHJQYOFCFNVZTYSJVTDBSXBTAPQWNKBEOZRWYBYMZQWRPGSBAGDEONBSCPFUZWQTLDYFMWKVNCYLKBUUEKBCNTFVZSWWWWDPRLTBBMMNFELSCNCMICTKXGMNBIHFA9YIJYPOMVKAY9CLXFQN9AIXIHHOXJXQIFESXKKOAKHMAJXQWNPLRFWW9BZF9CFMKQMAMNSKDCBJVUHTMOKWNFNQOSRJTCOXJSEZENVRPNOOARXUV9RMVK9EOCLSJCTRALFDPNNIQH9BGR9VLIIAKABZVUDBXJX9XTWTXJVVF9ZJPQWVOENOWGDMSKAPHMLMQGXXH9LTWHL99HGXTRDFR9ARYLBNEHTXJJOHRUAADM9CLDENRBWHBQEKH9JMVONHRZDSWW9IBNMYEZUSJAUWKSYPTCLISOBTEDNZAM9ISQYFMQENIEMDS9TIXGRQ9XZZSXPNISOFYVDQFVLNJVZYWZTMSLKTGJ9KIWSQCRBKZCDNMOLVPRGSOWGCLCUTAFMXQFQUTVNGHYYITAVABDINXWPKJQPODUKOMHEVBYPYPFJXPTDOLMAKPPUYJFQNQCAHOVPJK9UQTITMBHHUKWIEC9HYLGCZIADKQLV9GQHSGHMUEDJYDAEVJZA9BHSTMWVIVMJOYPLWEAOLRHRSXIJYTTQEFWRSXOGYSCFXOCXQJFVGJSNAUIRNBVWK9QDCGYQQWPKFAMBNXGTIHDJNSNZXRQSDJAIUF9UQY9HWYJGDHAH9UWUSAPEQADUCPHOVOCJGWFGDVFOUYOQXVWPVQCLJWYM9NHJQYCPTLGFXQOSJNHBKLTKHHGFPYXZEIOIAHWMQ9ZZZVBCBE9MIKJPOB9GOMWVSASBCFREOVIP9OHDQGVPBDJJPJHKECVOWKEXGWIGLZNFAFWFVJNXDWQKCWLPBQDZHLSKKC9QDNNDSOGMFDW9PUYEQEXRPJTO9XQNUFCFZBLNYJAGFLJSZKLA9DSQOOHDUDVKXDBNOKVNDXJEYCKYGOSYKAADXK9MRQMZJTKZESBRFINQXTQNEDYXBPVUQHCKELFZRVQFAYT9RHNXFLIPAVVOAPXSVHOZMFKRLMSLUOKZ9WOAIIXOGREMQNJEDIEAXNRMYJVWMPTDHUDCNYXWOONDKQPNNYPVXLXEDZKMJIVHKLCLMHVOMVOOLKNCOM9TRNQNVCGPIAP9LMOUEIUMK9XAHNKIYRVTMLIKTZMURVCNHKVQYPFGDFP9BGGTEGSIJPWBA99WCRIGOKTXHZIWPRCHRINBLRQMGZBLXXFNMKHSOYZBPJBBALUCARASVGUSWDOPAEONUVXC9NCKWKVCCUDBB9PNRQXGAK9DSQDIMBWVERXTCHMSSMHJTSCLJJB9CSSANZDQQFRRGLNUKTQIHIYHDVBNQRYBAJIDOYSMYYOJYUAZCWDZIPOFFE9AHICXMTQELNBWKPBXQUOXBFHYIMMLSGBATONCY9IAIKPGEG9KHCBUVGXJLSDGVJSUI9GBR9WDMFJNZWXLLPVNXFYFPTWRBNKWVHGJKKUBWYWAYWBZUEJEDDGLXHVRXRBMFWQVGBNALNNHGPGGIWLJHSOX'
        b'YYKM9AOPBSOSKZJRE9LIUNGFEBPWAK9JQD9LNKVLLOBVYTDQ9QMRNWJHWGTBFLCCYPQ9B9YMJMORDVGDCCVYAQOYFVGZKYUKXTLLUVWNRKIBYZEQFLYRWYRZNWKJAGVWO9VDRSYCAOARINNIL9EQKBREAGEZMBIXSZKVWRRNRLUYAYYUZUYHW9DUJJKJQVMJCPZFBLAURYJGZLT9ZHBLNUQWE9YVJFMWWZNJRHFSPVCQKJMWUCYPYUBHA9QEPCFAYWMGQOFDLZXDQSPYSSDL9MKJAPUGQWGAIRJC9MEYNTMABQTKVIHLSYSNSWAZGJL9YLIZWIO9G9LNRNENQHVZK9YXNQTJSFIJQPLVWWCJ9UTEEYGVFJVUVBJPHKBZACPVQFQCQAVDV9BUTXLFQSHIXZTEONSVKECHCVICRRUZGIPGEFMGUK9QQOPKMYHTDPIIKKDELF9DGSBBEHESJETZSPYTXSAPYA9ZSRKHECXXT9TTKSRIMRFKBBHFKQIYIJGJNSTZRGORHZLVEVLGGXTUHBEDGFIEVFZBQDCNJPQQ9DXMPP9KJD9PBZWKUT9ZPYW9FHBSSNSVTTGHSEVIHYFSUCIRDXSHWCOOGPTTJCCFNHYLRQHRQOBVNUNROWRSYQATJCSSYUGZ9YWFNJHIQNZMIGYKPDFR9JXMAJHQIR9PEWZRHYMOVJNQUXHKNRZEIJMQOZIQVOUSNEQRCYEIAVMHHUA9XIG9CQSBYCDQGEHHZPGSQCHY9OIBBSHSGTORMXIUAXERVPBZ9OGHBCDRXOUFNFJDKALLQOQFMWHHIPJSOAQTHUUFJWCTCROCFSYLOBHIYWCFJQHGWSGGKJRSKZGNUBDMGQZZM9SEZQXABXYFROYUYOHJEPPGCLCWOTZZGYVTBZH9AWPCVGILCDUWRQVLPDEJLVUKNNKBFFXSMVTAIZGBBJMMOAHGLMASBICFUQKWAKHEVNDQPNHDXSJFYGQOVWOKTWDSRGWCWNF9KP9VFOCTED9LIDRIPBLBMWUGRUIPENOFHSATAKHBRHQFDDEOZOZSDZKZWYNWDXVEMRASWCVMFNESLVUIFQNXXDABDGBBUICOZRAADRKQHRYRD9PVTWAETJCAOQIRNZGSULUWMZIVQZR9WDZVBAQXWBFPQRINPKDHGIMWMEOHOKODFSO9DSEZOPAWFLIYBUZWP9OYSTWFNKEFWYGPUTEZOGDKMZCQOYNTEONUSNSBNBMMPFGFTCUID9AELBVGZHYTJ9VSUQLFZDYYOCBMFYHFNFPOLUHGTLFXRWD9JUHFTU9DMSALSARRPYVHDEQTGY9TYTRUHD9YWCZFUTNNJPPRSZPPARMVKWVRMFIEGVJYXEMQTCDGZPAFHNIJTNPZYVGT9RQWKBZZ9CKRKAFMKGDKXGJUZHMDNWUPZYLDDVSORPMCCDLPGIIIYAVDLJODEVRPQIA9JLSEYQTIGDTNGYRNVIQBFBFLYVHDUORTCFFIWOBQJXQ9NUXAHI9TUVR9SJKTST9MGJIIBGDIFRELOHDW9MXPARDLG9WQWLIC9TTHVOSQ9FCAFDCSUHHISCWVJNYWHKVMPYBKVORHRGVY9PDHXPNDXIMJMYECYQZGDT9DANTQBJPXHN9MG9MDKJ9EJIDQZFLJX9VPACAHZUXMBMPRUGNHBXFCGBDYUWAIPFVAMQZYMLESKEEIKFWQVPJRBQBCDOYVSUFTONAIHMIUEVPXTWUYADPQLMBLKWCYXETFVLTZZATEHYDTHSDXAJMQDLKYNQNUAZBVYRLCVKAOUWA9QHXK9AXYFZGBUAZLVZGLVRKSHVRLXTYKMPDCZURJOSTHVJFCKIXHXXQQNCBTAEXUVMKMKEQVUPOEEY9LSTKT9XNJVJPRK9ZDUFQWTMJHWNMTTDRCRMFRXUEZMYXLQEAQMEV9MBIORUONCARJVMCDIR9PIOUJUXIDFY9NHCENUCVPJDIKHIRVRFPGKDZSIGZSBZGTRWAXLRFQLESYXKUISYBTWGZPAVNIKVXLYGINAUMZSJAMDRM9LVAXXCBSOBXUAKFAPMVAXDPFZTKWQCEOKBKAJWELYR9ZEWOTTNFOLHCNUPNMJO9CBH9HXTKFCSXMGBVHY9QFLDFNYMGQUEOXMEPBZWTOKHUMFIJKLUMYPZJHNKIBTRCDSNRBFOSPMDMYCRTBQJZZASRRNIOZTAZ'
        b'JZXMMJLJOODDZHQLMRVW9FNQHWGIXOWXW9CDZMZESYXSN9DGTHFGFOMZERPNHVE9VLYJRSSGLYMPTXAS9WWJWIUVCTU9GWQBL9WLXWNWXMDLSSXATMFRS9KNNJIGIJNSGYUMPNUHQTWNPCGISJWXTKSVKTCWKR9PCCYQUL9HCOFMHMVFYIPH9BENPKVLDU9RIDXTEWSVPMCXPCQ9ULMYFLHNOZVXGJZPIMQJPXAGXSOIOPYYVGDRVSGEBZJGTYTBLRKMQ9DANLRBLLWFKXCIELBTHYFTJTYEWVIEIQKIXMJAEFWRYXYDE9CCVGQCQUUOKZJ9BYNGIBOYY9CVGGIBIUPLMMFCFEPDTHBKVPNNJBKZJWDDQVZFXREWVNLDEZMUJCOXP9SZDFLVWJDHOKGIWGUXXIAMYUOVDGKWQGFEIHFQAWVELDWKCG9FCKVQ9WGLSHERYCPORNXISPGAYBNKXXN9LSGMU9J9NUMMXARUBKBBTFBJMCUWGNOQCGOMLKYUPTKJHMRZCZC9PBHJEBPQJMSJUSWZVTGPYSR9GTASEIHLDPSPQOQJ9LZOQRPUHNJYCFRMVURJEXQSLKHQECVJ9J9ORFVB9QVBGSRCJTDKJJZWHDDDERTYFHDSJYAQEIIQKJT9MJOYXJHANHPJD9ZBEJHPGHVHTBLRQWQSBNLHUDQUHDBH9UP9LURGHMINB9YHIQTACNDCNXDDURRDJMYUSMFMYX9XWD9DCRCKFEYIWPESUPKRNVKPTORTHHZUILKBYRCSADDFNEJ9HQEZPHHYWDJLDXMEMMDEEHUJU9AGF9USJLKWRZPBYIICMPSJXNMVPFEDILRMANTUULXXHU9L9FNVTIB9ZUGXTLICOQUNIWTGFHNMNNUMOBMKLIWLVHBYKMKSSCIDO9TMAYERDGMUSQTNPUJLLAYYQT9HZTNWOXG9WYUNMFHXGXVAQHFHDXEEEXAASFOSARACI9HCWYTKJJFDLQUJ9WBJCWQUJCCHAWANLTZWZBDSIPLOAGNPPHJMONDSZ9AFQTPYZSKCZEBXRGUKPEMVXU9CIIWIQVTKSNBTOFWLDEPFFQCANZ9JCXXWXIWNCWQZRQQQLPYSWKL9YGNEQUXYOXYLZVRIQ99BQJJUOWPPHGKSXMRAZMOMSMKOXOFODLQAPHJPFY9VWNMFGWODDMWCBFRUMFCNSAGVNGIODRFVWYDWSOYXCMCCKIWXJZIL9TFPBOWEW9ORIZOYKDWZHVEKXZURPOUHLYSOIEKKXMIRCLXJSHALHZO9ZPFID9GBODDJZPPMWCMWPIWYTMAPDM9JUNJCJMVHDPBCCRWJHA9IQBTZHQKUUROLCSRTIAROZQPJXBCLYEP9H9PGSVGJVHKIAWRZDVCZIXUGHONGJ9LEHVNXHZNAIPJJZVEWJOMOUFJZSHEBXIZVEMKLK9IFJKDHUXTZD9DIYVPYPTVGBIGINYJVH9KQOWWCEOQBQIMKOC9FTAUMEHYMQEYKZFBGHZYLCDJCGXV9DTKXPZDHIFONHSDSRCMVXSRIIWFXLFB9VFUOEYYKEKGAZJVJHHNYEJCMQOGRIBKJVAHRPTTUALKBETUYDWSNT9IYEVMDYR9SJGMLG9EIKZYDIUXWRXJSZCOMODCRZJTRWTSUHSPNJUASRTDQBEJBONIPKHUSHVVZ9TWZNCVMJVJASSBMX9VAEQJTCW9DBEQSDBUMQOYWIYTKFFBEWHGUAWAGMPMGYUFUQDCNORFBFUJZPSJQLM9ORMRBFZUZGVZTNJHC9FZPICGT9WOHJANEPPM9SNZBEJRDKENYYVLDCLCZIAHWVNAJIGP9MQAQLVHEJKQGSOAGFPYOKPNEBQYVVVQCBTDZXIIXZDCSFHWWTOUTWKSBVMUMWCSSQWHCMWKJGTREMSMBP9ADHFLKAHNFQSWUOMOYARDBPUDZDPGIGRAGBZQJAMHDNU9GDXUGQHDBWXKGZAAVXSZXUWHEKSSRRBXTGHUKUZPVCBSKQNDCOTWVXOKBFWKULVXRLUTNPRULDQJNZKAEFAOX9EUZSRJPPRFO9PDQUKXUNLILADQDGMMYJACOUZCKEK9PDEIMNBDIBGMTABALXJBHQTPXRVXUQDJBLUA9QF9AEQHA9LMUFUQQQOUSMQUGGPSLBWTKGXGVHPAX9SI9ITDCMYWHRONTXMBRUOGGPUYLDZFOGZC',
      )

    self.assertEqual(
      key.get_digest(),

      # Note that the digest is 3 hashes long, because the key
      # is 3 fragments long.
      TryteString(
        b'DMQBKFFAGMHSOGLQDYOGTZ9G9NZYSE9JPEAHV9WGAKENOWLVGZJLBIRIKLKQINKKUQ9JDJYGPJYYDTTMW'
        b'TIBCVWNGKLYX9UDSNQK9FWFODLGWOZREMZYWYRPILH9LYLOSRJSZQKKXBBEGVRJYTFHWQXRAMPMRJJT99'
        b'KXGAKZZZVNRPQ9ELDPAMOMJOIGOKCRWHLBIURDRVSWLEQLFVFXKCSNSTWQJDDV9YZFHBWDEIXM9VGGIFD',
      ),
    )

    # Did you notice that the key fragment and corresponding digest
    # from the previous test also appear in this one?
    #
    # Each fragment is processed independently, which is critical for
    # multisig to work correctly.
