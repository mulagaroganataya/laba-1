from uuid import uuid1


class Cards:
    def __init__(
        self,
        user_id: str = None,
        number: int = None,
        date: str = None, 
        csv: int = None
    ):
        try:
            if not all(
                [
                    user_id is None or isinstance(user_id, str),
                    number is None or isinstance(number, int),
                    date is None or isinstance(date, str),
                    csv is None or isinstance(csv, int),
                ]
            ):
                raise TypeError
            self.id = str(uuid1())
            self.user_id = user_id
            self.number = number
            self.date = date
            self.csv = csv
        except TypeError:
            print("Error: something wrong with types")
            return False
        except:
            print("Error with init Cards")

    def update(self,number: int = None,
        date: str = None, 
        csv: int = None) -> bool:
        result = True
        try:
            if not all(
                [
                    number is None or isinstance(number, int),
                    date is None or isinstance(date, str),
                    csv is None or isinstance(csv, int),
                ]
            ):
                raise TypeError
            if number:
                self.number = number
            elif date:
                self.date = date
            elif csv:
                self.csv = csv
            else:
                result = False
        except TypeError:
            print("Error: something wrong with types")
            return False
        except:
            result = False
        return result

    def delete(self): 
        result = True
        return result