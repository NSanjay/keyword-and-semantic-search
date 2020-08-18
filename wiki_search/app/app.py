from flask import Flask, render_template, request
from search_util import SearchUtil

search_util = SearchUtil()
app = Flask(__name__)

@app.route("/")
def landing_page():
    return render_template("landing.html")

@app.route("/search", methods=["POST"])
def search_results():
    query = request.form["query"]
    sanitised_query = query

    if not search_util.check_query(query):
        return render_template("noResults.html", query=query)

    final_hits = search_util.retrieve_top_k_hits(sanitised_query)
    return render_template("searchResults.html", hits=enumerate(final_hits), query=query)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
