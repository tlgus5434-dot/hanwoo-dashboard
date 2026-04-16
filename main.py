import os
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

API_KEY = '0d14fafa91c08020cfea568cf28cef3bccbb2074fee206a54fe5421537fc2fc2'
EKAPE   = 'http://data.ekape.or.kr/openapi-data/service/user/grade'
PORT    = int(os.environ.get('PORT', 8000))

HTML = open('index.html', 'rb').read()

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == '/' or parsed.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML)

        elif parsed.path.startswith('/api/'):
            self.handle_api(parsed)

        else:
            self.send_error(404)

    def handle_api(self, parsed):
        params = dict(urllib.parse.parse_qsl(parsed.query))
        endpoint = parsed.path[5:]
        ep_params = {'ServiceKey': API_KEY}

        if endpoint == 'liveGrade':
            ep_params['auctDate'] = params.get('date', today())
            if params.get('abatt'): ep_params['abattCd'] = params['abatt']
            ekape_ep = 'liveauct/cattleGrade'

        elif endpoint == 'priceDetail':
            ep_params.update({
                'startYmd': params.get('start', month_start()),
                'endYmd':   params.get('end',   today()),
                'breedCd':  '024001',
                'sexCd':    params.get('sex', '025003'),
                'defectIncludeYn': 'Y',
            })
            if params.get('abatt'): ep_params['abattCode'] = params['abatt']
            ekape_ep = 'auct/cattlePriceDetail'

        else:
            self.send_error(404); return

        qs  = urllib.parse.urlencode(ep_params)
        url = f'{EKAPE}/{ekape_ep}?{qs}'

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as res:
                data = res.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, fmt, *args):
        if '/api/' in (args[0] if args else ''):
            print(f'[API] {args[0]}')

def today():
    from datetime import date
    return date.today().strftime('%Y%m%d')

def month_start():
    from datetime import date
    d = date.today()
    return d.replace(day=1).strftime('%Y%m%d')

print(f'서버 시작: 포트 {PORT}')
HTTPServer(('', PORT), Handler).serve_forever()
