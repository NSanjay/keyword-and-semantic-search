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
    # is_valid, sanitised_query = search_util.sanitise_query(query)

    # if not is_valid:
    #     return render_template("noResults.html", query=query)

    # print(sanitised_query)
    final_hits = search_util.retrieve_top_k_hits(sanitised_query)
    # print(final_hits)
    return render_template("searchResults.html", hits=enumerate(final_hits), query=query)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
