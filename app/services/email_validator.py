"""
Email validation service.
Blocks disposable, temporary and flagged email domains.
"""

BLOCKED_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', 'guerrillamail.net', 'guerrillamail.org',
    'guerrillamail.de', 'guerrillamail.info', 'guerrillamail.biz', 'grr.la',
    'sharklasers.com', 'guerrillamailblock.com', 'spam4.me', 'yopmail.com',
    'yopmail.fr', 'cool.fr.nf', 'jetable.fr.nf', 'nospam.ze.tc', 'nomail.xl.cx',
    'tempmail.com', 'temp-mail.org', 'temp-mail.io', 'throwam.com', 'throwam.net',
    'trashmail.com', 'trashmail.me', 'trashmail.net', 'trashmail.at',
    'trashmail.io', 'trashmail.xyz', 'trashmailer.com', 'trash-mail.at',
    'dispostable.com', 'mailnull.com', 'spamgourmet.com', 'spamgourmet.net',
    'spamgourmet.org', 'spamspot.com', 'spamthis.co.uk', 'spamtrap.ro',
    'spamtraps.net', 'mailnesia.com', 'maildrop.cc', 'mailsac.com',
    'mailscrap.com', 'mailshell.com', 'mailtemp.info', 'mailtemp.net',
    'mailzilla.com', 'mailzilla.org', 'mytrashmail.com', 'neomailbox.com',
    'nepwk.com', 'nervmich.net', 'nervtmich.net', 'netmails.com',
    'netzidiot.de', 'nnot.net', 'no-spam.ws', 'nobulk.com',
    'noclickemail.com', 'nomorespamemails.com', 'nonspam.eu', 'nonspammer.de',
    'noref.in', 'nospam4.us', 'nospamfor.us', 'nospammail.net',
    'notmailinator.com', 'nowmymail.com', 'objectmail.com', 'obobbo.com',
    'odaymail.com', 'odnorazovoe.ru', 'oneoffmail.com', 'onewaymail.com',
    'opentrash.com', 'otherinbox.com', 'outlawspam.com', 'owlpic.com',
    'pjjkp.com', 'pookmail.com', 'privacy.net', 'privatdemail.net',
    'proxymail.eu', 'putthisinyourspamdatabase.com', 'recyclemail.dk',
    'regbypass.com', 'rejectmail.com', 'rmqkr.net', 'rootfest.net',
    'safe-mail.net', 'safetymail.info', 'safetypost.de', 'sandelf.de',
    'saynotospams.com', 'selfdestructingmail.com', 'sendspamhere.com',
    'sharedmailbox.org', 'shitmail.me', 'shitmail.org', 'shortmail.net',
    'sibmail.com', 'sinnlos-mail.de', 'slopsbox.com', 'smashmail.de',
    'snakemail.com', 'sneakemail.com', 'sneakmail.de', 'snkmail.com',
    'sofimail.com', 'sofort-mail.de', 'sogetthis.com', 'spam.la',
    'spam.su', 'spamavert.com', 'spambob.com', 'spambob.net',
    'spambob.org', 'spambox.info', 'spambox.us', 'spamcannon.com',
    'spamcannon.net', 'spamcero.com', 'spamcon.org', 'spamcowboy.com',
    'spamcowboy.net', 'spamcowboy.org', 'spamday.com', 'spamex.com',
    'spamfree.eu', 'spamgoes.in', 'spamherelots.com', 'spamhereplease.com',
    'spamhole.com', 'spamify.com', 'spaminator.de', 'spamkill.info',
    'spaml.com', 'spaml.de', 'spammotel.com', 'spammy.host',
    'spamoff.de', 'spamslicer.com', 'spamstack.net', 'spamthisplease.com',
    'spamtroll.net', 'spoofmail.de', 'squizzy.de', 'squizzy.eu',
    'squizzy.net', 'startkeys.com', 'stopspam.app', 'stuffmail.de',
    'supergreatmail.com', 'supermailer.jp', 'superrito.com', 'suremail.info',
    'tafmail.com', 'talkinator.com', 'teewars.org', 'teleworm.com',
    'teleworm.us', 'tempalias.com', 'tempe-mail.com', 'tempemail.biz',
    'tempemail.com', 'tempemail.net', 'tempinbox.co.uk', 'tempinbox.com',
    'tempmail.eu', 'tempmail.it', 'tempmail.pp.ua', 'tempmail.us',
    'tempmail2.com', 'tempmaildemo.com', 'tempmailer.com', 'tempmailer.de',
    'tempr.email', 'tempsky.com', 'tempthe.net', 'tempymail.com',
    'tfwno.gf', 'thanksnospam.info', 'thc.st', 'thedoghousemail.com',
    'thisisnotmyrealemail.com', 'thismail.net', 'throwaway.email',
    'throwaymail.com', 'tilien.com', 'tittbit.in', 'tizi.com',
    'tmailinator.com', 'toiea.com', 'toomail.biz', 'torchmail.com',
    'tradermail.info', 'trash2009.com', 'trash2010.com', 'trash2011.com',
    'trashcanmail.com', 'trashdevil.com', 'trashemail.de', 'trashimail.com',
    'trashmalware.com', 'trashmails.com', 'trashspam.com', 'trayna.com',
    'trbvm.com', 'trbvn.com', 'trickmail.net', 'troll-mail.com',
    'tryalert.com', 'turual.com', 'twinmail.de', 'txcct.com',
    'uggsrock.com', 'unids.com', 'unimark.org', 'unmail.ru',
    'uroid.com', 'us.af', 'veryrealemail.com', 'viralplays.com',
    'vpn.st', 'vsimcard.com', 'vubby.com', 'walala.org',
    'walkmail.net', 'walkmail.ru', 'webemail.me', 'webm4il.info',
    'webuser.in', 'wee.my', 'weg-werf-email.de', 'wegwerfemail.com',
    'wegwerfemail.de', 'wegwerfmail.de', 'wegwerfmail.info',
    'wegwerfmail.net', 'wegwerfmail.org', 'wegwerfnummer.de',
    'welikecookies.com', 'wh4f.org', 'whopy.com', 'whyspam.me',
    'wickmail.net', 'wilemail.com', 'willhackforfood.biz',
    'willselfdestruct.com', 'winemaven.info', 'wmail.cf',
    'wolfsmail.tk', 'wollan.info', 'worldspace.link', 'wralmail.com',
    'wuzupmail.net', 'xagloo.co', 'xagloo.com', 'xemaps.com',
    'xents.com', 'xjoi.com', 'xl.cx', 'xmail.com', 'xmaily.com',
    'xoru.net', 'xoxy.net', 'xperiae5.com', 'xram.io',
    'xsmail.com', 'xyzfree.net', 'yapped.net', 'ycare.de',
    'yesey.net', 'yodx.ro', 'yogamaven.com', 'yopmail.gq',
    'yopmail.net', 'yopmail.org', 'yuoia.com', 'z1p.biz',
    'za.com', 'zebins.com', 'zebins.eu', 'zehnminuten.de',
    'zehnminutenmail.de', 'zetmail.com', 'zhorachu.com',
    'zipsendtest.com', 'zoemail.com', 'zoemail.net', 'zoemail.org',
    'zomg.info', 'discard.email', 'discardmail.com', 'discardmail.de',
    'fakeinbox.com', 'fakemailgenerator.com', 'fakemail.net',
    'filzmail.com', 'filzmail.de', 'fizmail.com', 'fleckens.hu',
    'fmailbox.com', 'fmailc.com', 'fmailix.com', 'frapmail.com',
    'front14.org', 'fuckingduh.com', 'fudgerub.com', 'fun2.biz',
    'furzmail.de', 'fux0ringduh.com', 'garliclife.com',
    'gehensieschnell.de', 'gelitik.in', 'get1mail.com', 'get2mail.fr',
    'getairmail.com', 'getairmail.cf', 'getairmail.ga', 'getairmail.gq',
    'getairmail.ml', 'getairmail.tk', 'getfun.men', 'getmails.eu',
    'getonemail.com', 'getonemail.net', 'ghosttexter.de', 'giantmail.de',
    'gishpuppy.com', 'glubex.com', 'glutglut.com', 'gotmail.com',
    'gotmail.net', 'gotmail.org', 'grabmail.com', 'greensloth.com',
    'guerillamail.biz', 'guerillamail.com', 'guerillamail.de',
    'guerillamail.info', 'guerillamail.net', 'guerillamail.org',
    'gustr.com', 'h8s.org', 'hailmail.net', 'harakirimail.com',
    'hartbot.de', 'hatespam.org', 'herp.in', 'hidemail.de',
    'hidzz.com', 'hmamail.com', 'hopemail.biz', 'hotpop.com',
    'humaility.com', 'ieh-mail.de', 'ihateyoualot.info',
    'iheartspam.org', 'ikbenspamvrij.nl', 'imails.info', 'inbax.tk',
    'inbox.si', 'inboxalias.com', 'inboxclean.com', 'inboxclean.org',
    'inboxproxy.com', 'incognitomail.com', 'incognitomail.net',
    'incognitomail.org', 'insorg-mail.info', 'instant-mail.de',
    'instantemailaddress.com', 'instantlyemail.com', 'ip6.li',
    'ipoo.org', 'irabops.com', 'irish2me.com', 'isnotspam.com',
    'jetable.com', 'jetable.net', 'jetable.org', 'jnxjn.com',
    'junk1.tk', 'junkmail.com', 'junkmail.ga', 'junkmail.gq',
    'kasmail.com', 'kaspop.com', 'keepmymail.com', 'killmail.com',
    'killmail.net', 'klassmaster.com', 'klassmaster.net', 'klzlk.com',
    'koszmail.pl', 'kurzepost.de', 'laoeq.com', 'laoho.com',
    'lazyinbox.com', 'letthemeatspam.com', 'lhsdv.com', 'libox.fr',
    'lifebyfood.com', 'lol.ovpn.to', 'lolfreak.net', 'lookugly.com',
    'lortemail.dk', 'losemymail.com', 'lovemeleaveme.com', 'lr78.com',
    'lroid.com', 'lukop.dk', 'maboard.com', 'mail-filter.com',
    'mail-temporaire.fr', 'mail2rss.org', 'mail333.com',
    'mailbidon.com', 'mailbiz.biz', 'mailblocks.com', 'mailbucket.org',
    'mailc.net', 'mailcat.biz', 'mailcatch.com', 'mailchop.com',
    'mailcker.com', 'mailde.org', 'mailde.de', 'mailde.info',
    'maileater.com', 'mailed.ro', 'maileimer.de', 'mailexpire.com',
    'mailf5.com', 'mailfail.com', 'mailfall.com', 'mailforspam.com',
    'mailfree.ga', 'mailfreeonline.com', 'mailfs.com', 'mailguard.me',
    'mailhazard.com', 'mailhazard.us', 'mailhex.com', 'mailimate.com',
    'mailin8r.com', 'mailinater.com', 'mailinator.com', 'mailinator.net',
    'mailinator.org', 'mailinator.us', 'mailinator2.com',
    'mailincubator.com', 'mailismagic.com', 'mailismagic.net',
    'mailjunk.cf', 'mailjunk.ga', 'mailjunk.gq', 'mailjunk.ml',
    'mailjunk.tk', 'mailkutu.com', 'mailmate.com', 'mailme.gq',
    'mailme.ir', 'mailme.lv', 'mailme24.com', 'mailmetrash.com',
    'mailmoat.com', 'mailms.com', 'mailnew.com', 'mailnull.com',
    'mailsac.com', 'guerrilla-mail.com', 'throwam.com',
}

WHITELIST_MODE = False
ALLOWED_DOMAINS = {
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'live.com',
    'icloud.com', 'me.com', 'mac.com', 'protonmail.com', 'proton.me',
    'tutanota.com', 'zoho.com', 'aol.com', 'msn.com', 'yandex.com',
    'mail.com', 'gmx.com', 'gmx.net', 'fastmail.com', 'hey.com',
}


def is_valid_email_domain(email):
    """
    Validate email domain.
    Returns (is_valid, error_message)
    """
    if not email or '@' not in email:
        return False, 'Invalid email format.'

    parts = email.strip().lower().split('@')
    if len(parts) != 2:
        return False, 'Invalid email format.'

    domain = parts[1].strip()

    if not domain or '.' not in domain:
        return False, 'Invalid email domain.'

    if domain in BLOCKED_DOMAINS:
        return False, 'Disposable or temporary email addresses are not allowed. Please use a real email.'

    for blocked in BLOCKED_DOMAINS:
        if domain.endswith('.' + blocked):
            return False, 'Disposable or temporary email addresses are not allowed. Please use a real email.'

    if WHITELIST_MODE and domain not in ALLOWED_DOMAINS:
        return False, 'Only emails from trusted providers are accepted (Gmail, Yahoo, Outlook, ProtonMail, etc.)'

    return True, ''
def validate_email(email):
    """
    Wrapper around is_valid_email_domain for import compatibility.
    Returns (is_valid, error_message)
    """
    return is_valid_email_domain(email)