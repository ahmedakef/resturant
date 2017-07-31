from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database_setup import Base, Restaurant, MenuItem
#from flask.ext.sqlalchemy import SQLAlchemy
import datetime
import json

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/"):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('location', '/restaurants')
                self.end_headers()
                print("\nredirect to /restaurants\n")
                return


            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                result = session.query(Restaurant.name,Restaurant.id).order_by(Restaurant.name.asc()).all()
                output = ""
                output += "<html><body>"
                output += "<h1>here is all restaurants :</h1>"
                output += '''<a href="restaurants/new" > add new </a>'''
                for item in result:
                    output+="<h3>"
                    output += item[0]
                    output+="</h3>"
                    output+='''<a href="/restaurants/%s/edit">edit</a></br>''' % item[1]
                    output+='''<a href="/restaurants/%s/delete">delete</a></br>''' % item[1]
                    output+='''<a href="/restaurants/%s/menu/JSON">json</a></br></br>''' % item[1]

                output += "</body></html>"
                self.wfile.write(output)
                print ("\nrender the /restaurants page\n")
                return


            if self.path.endswith("/JSON"): #/restaurants/<int:restaurant_id>/menu/JSON
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurantID = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(id=restaurantID).one() # you may use it in the future
                items = session.query(MenuItem).filter_by(
                        restaurant_id=restaurantID).all()
                output= json.dumps([i.serialize for i in items])
                self.wfile.write(output)
                print ("\n output the json items\n")
                return


            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>'''
                output += '''<h2>add new restaurant ?</h2>'''
                output += '''<input name="newRestaurantName" type="text" >'''
                output += '''<input type="submit" value="Add resturant"></br></br> '''
                output += '''<button href="/restaurants"> back </button> </form> '''
                output += "</body></html>"
                self.wfile.write(output)
                print ("\nrender the /restaurants/new page\n")
                return

            if self.path.endswith("/edit"):
                restaurantID = self.path.split("/")[2]
                myrestaurant = session.query(Restaurant).filter_by(id=restaurantID).one()

                if myrestaurant :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>%s</h1>" % myrestaurant.name
                    output += '''<form method='POST' enctype='multipart/form-data' action="/restaurants/%s/edit">''' % restaurantID
                    output += '''<h2>Edit restaurant name ?</h2>'''
                    output += '''<input name="newRestaurantName" type="text" value="%s" >''' % myrestaurant.name
                    output += '''<input type="submit" value="Change name"></br></br>'''
                    output += '''<button href="/restaurants" > back </button>  </form>'''
                    output += "</body></html>"
                    self.wfile.write(output)
                    print ("\nrender the /restaurants/<id>/edit page\n")
                    return
            if self.path.endswith("/delete"):
                restaurantID = self.path.split("/")[2]
                myrestaurant = session.query(Restaurant).filter_by(id=restaurantID).one()

                if myrestaurant :
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>do you want to remove %s ?</h1>" % myrestaurant.name
                    output += '''<form method='POST' enctype='multipart/form-data' action="/restaurants/%s/delete">''' % restaurantID
                    output += '''<input type="submit" value="Delete"></br></br>'''
                    output += '''<button href="/restaurants"> back </button> </form> '''
                    output += "</body></html>"
                    self.wfile.write(output)
                    print ("\nrender the /restaurants/<id>/edit page\n")
                    return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                #insert into the database
                newrestaurant = Restaurant(name=messagecontent[0])
                session.add(newrestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('location', '/restaurants')
                self.end_headers()
                print("\nredirect to /restaurants after adding new restaurant\n")

            if self.path.endswith("/edit"):
                print("\nrecieve post request\n")
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantID = self.path.split("/")[2]
                    print("\nrecieve multipart/form-data\n")
                    print("resturant ID is %s" % restaurantID)

                    #Edit the row in the database
                    myrestaurant = session.query(Restaurant).filter_by(id=restaurantID).one()


                    if myrestaurant:
                        myrestaurant.name = messagecontent[0]
                        session.add(myrestaurant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('location', '/restaurants')
                        self.end_headers()
                        print("\nredirect to /restaurants after editting restaurant name\n")

            if self.path.endswith("/delete"):
                print("\nrecieve post request\n")
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    restaurantID = self.path.split("/")[2]

                    #remove the row from the database
                    myrestaurant = session.query(Restaurant).filter_by(id=restaurantID).one()


                    if myrestaurant:
                        session.delete(myrestaurant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('location', '/restaurants')
                        self.end_headers()
                        print("\nredirect to /restaurants after deleteing restaurant name\n")
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on http://127.0.0.1:%s/restaurants" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
