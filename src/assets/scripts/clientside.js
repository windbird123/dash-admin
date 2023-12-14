window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        syncFunction: (n_clicks) => {
            let json = sessionStorage.getItem("state");
            return JSON.parse(json);
        },
        createSortable: (value) => {
            // 개발시 Sortable.js 를 명시적으로 import 하지 말고 (예: import Sortable from "...")
            // npm install sortablejs 로 Local 에 패키지를 인스톨하면 code auto-complete 등이 된다.
            Sortable.create(items, {
                animation: 150,
                group: "state",
                dataIdAttr: "id",
                store: {
                    get: (sortable) => {
                        let order = sessionStorage.getItem(sortable.options.group.name);
                        return JSON.parse(order);
                    },
                    set: (sortable) => {
                        let order = sortable.toArray();
                        sessionStorage.setItem(sortable.options.group.name, JSON.stringify(order));
                        document.getElementById("hidden_sync_button").click();
                    }
                }
            });

        }
    }
});
