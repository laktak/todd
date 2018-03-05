class KeyBindings:
    user_keys = []
    key_bindings = {}

    def __init__(self, user_keys):
        self.user_keys = user_keys
        self.fillWithDefault()
        self.fillWithUserKeys(user_keys)

    def fillWithUserKeys(self, users_keys):
        for bind in users_keys:
            key = self.userKeysToList(users_keys[bind])
            try:
                self.key_bindings[bind] = key
            except KeyError:
                print("KeyBind \"" + bind + "\" not found")

    def fillWithDefault(self):
        self.key_bindings["home"] = ["g"]
        self.key_bindings["end"] = ["G"]
        self.key_bindings["up"] = ["k"]
        self.key_bindings["down"] = ["j"]
        self.key_bindings["page-up"] = ["K"]
        self.key_bindings["page-down"] = ["J"]
        self.key_bindings["quit"] = ["q"]
        self.key_bindings["save"] = ["S"]
        self.key_bindings["reload"] = ["R"]
        self.key_bindings["archive"] = ["X"]
        self.key_bindings["undo-archive"] = ["U"]
        self.key_bindings["new"] = ["n"]
        self.key_bindings["toggle-done"] = ["x"]
        self.key_bindings["priority-higher"] = ["<"]
        self.key_bindings["priority-lower"] = [">"]
        self.key_bindings["edit"] = ["enter"]
        self.key_bindings["delete"] = ["D"]
        self.key_bindings["switch-context"] = ["c"]
        self.key_bindings["toggle-sort-order"] = ["s"]
        self.key_bindings["toggle-wrapping"] = ["w"]
        self.key_bindings["toggle-view"] = ["v"]
        self.key_bindings["toggle-help"] = ["?"]
        self.key_bindings["search"] = ["/"]
        self.key_bindings["search-clear"] = ["C"]
        self.key_bindings["add-due"] = ["+"]
        self.key_bindings["subtract-due"] = ["-"]

    def __getitem__(self, index):
        return ", ".join(self.key_bindings[index])

    def userKeysToList(self, userKey):
        keys = userKey.split(",")
        return [key.strip() for key in keys]

    def getKeyBinding(self, bind):
        try:
            return self.key_bindings[bind]
        except KeyError:
            return []

    def is_bound_to(self, key, bind):
        return key in self.getKeyBinding(bind)
