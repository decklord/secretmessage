class TastyModel(object):

    @classmethod
    def create_test_model(cls, data):
        model = cls(**data)
        model.save()
        return model
