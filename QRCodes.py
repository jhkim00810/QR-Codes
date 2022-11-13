
def divide_terms(coefficient1, power1, coefficient2, power2):
    
    new_coeff = z256.div(coefficient1, coefficient2)
    new_pow = power1 - power2

    divided = Polynomial()
    divided = divided.add_term(new_coeff, new_pow)
    return divided

class Polynomial:
    def __init__(self, terms=None):
 
        if terms != None:
            self._terms = dict(terms)
        else:
            self._terms = {}

    def __str__(self):
        
        term_strings = []
        powers = list(self._terms.keys())
        powers.sort(reverse=True)
        for power in powers:
            coefficient = self._terms[power]
            if coefficient != 0:
                if power == 0:
                    term_strings.append("%d" % coefficient)
                else:
                    term_strings.append("%d*x^%d" % (coefficient, power))

        terms_str = " + ".join(term_strings)
        if terms_str == "":
            terms_str = "0"
        return "Polynomial: %s" % terms_str

    def __eq__(self, other_polynomial):
        if not isinstance(other_polynomial, Polynomial):
            return False
        
        terms = other_polynomial.get_terms()

        for power, coefficient in terms.items():
            if coefficient != 0:
                if power not in self._terms:
                    return False
                if self._terms[power] != coefficient:
                    return False

        for power, coefficient in self._terms.items():
            if coefficient != 0:
                if power not in terms:
                    return False
                if terms[power] != coefficient:
                    return False

        return True

    def __ne__(self, other_polynomial):
        
        return not self.__eq__(other_polynomial)

    def get_terms(self):
        
        terms = dict(self._terms)
        return terms

    def get_degree(self):
       
        highest_power = 0
        for power in self._terms:
            if (power > highest_power) and (self._terms[power] != 0):
                highest_power = power

        return highest_power


    def get_coefficient(self, power):
        
        if power in self._terms:
            return self._terms[power]
        else:
            return 0

    def add_term(self, coefficient, power):
        
        terms = {}
        terms = self.get_terms()
        
        if power in self._terms:
            terms[power] = z256.add(self._terms[power], coefficient)
        else: 
            terms[power] = coefficient
        
        return Polynomial(terms)

    def subtract_term(self, coefficient, power):
        terms = {}
        terms = self.get_terms()
        
        if power in self._terms:
            terms[power] = z256.sub(self._terms[power], coefficient)
        else: 
            terms[power] = coefficient
        
        return Polynomial(terms)

    def multiply_by_term(self, coefficient, power):
        
        terms = {}
        
        for each in self._terms:
            terms[power + each] = z256.mul(self._terms[each], coefficient)
        
        return Polynomial(terms)

    def add_polynomial(self, other_polynomial):
      
        for each_1 in self._terms:
            other_polynomial = other_polynomial.add_term(self._terms[each_1], each_1)
        
        return Polynomial(other_polynomial.get_terms())
        
    def subtract_polynomial(self, other_polynomial):
        
        for each_2 in self._terms:
            other_polynomial = other_polynomial.add_term(self._terms[each_2], each_2)
        
        return Polynomial(other_polynomial.get_terms())
        
    def multiply_by_polynomial(self, other_polynomial):
       
        poly_0 = Polynomial()
        
        for each_3 in self._terms:
            multiplied = other_polynomial.multiply_by_term(self._terms[each_3], each_3)
            poly_0 = poly_0.add_polynomial(multiplied) 
        
        return poly_0

    def remainder(self, denominator):
      
        zero = False
        poly_1 = Polynomial(self.get_terms())
        denominator_degree = denominator.get_degree()
        self_degree = poly_1.get_degree()
        first_denom_coeff = denominator.get_coefficient(denominator_degree)
        
        while self_degree >= denominator_degree:
            if self_degree == 0 and denominator_degree == 0:
                zero = True
            first_self_coeff = poly_1.get_coefficient(self_degree)
            quotient = divide_terms(first_self_coeff, self_degree, 
                                    first_denom_coeff, denominator_degree)
            product = denominator.multiply_by_polynomial(quotient)
            poly_1 = poly_1.subtract_polynomial(product)
            self_degree = poly_1.get_degree()
            
            if zero:
                return poly_1
        return poly_1


def create_message_polynomial(message, num_correction_bytes):
  
    poly_2 = Polynomial()
    count = 0
    
    for each_4 in message:
        power = num_correction_bytes + len(message) - 1 - count
        count += 1
        poly_2 = poly_2.add_term(each_4, power)
    
    
    return poly_2

def create_generator_polynomial(num_correction_bytes):

    poly_3 = Polynomial()
    temporary = Polynomial()
    temporary = temporary.add_term(1,1)
    temporary = temporary.add_term(1,0)
        
    if num_correction_bytes > 0:
        poly_3 = poly_3.subtract_polynomial(temporary)
    for integer in range(1, num_correction_bytes):
        temporary = Polynomial()
        temporary = temporary.add_term(1,1)
        temporary = temporary.subtract_term(z256.power(2, integer), 0)
        poly_3 = poly_3. multiply_by_polynomial(temporary)
    
    return poly_3

def reed_solomon_correction(encoded_data, num_correction_bytes):
  
    generator = create_generator_polynomial(num_correction_bytes)
    message = create_message_polynomial(encoded_data, num_correction_bytes)
    remainder = message.remainder(generator)
    
    return remainder

# qrcode.start(reed_solomon_correction)--> Uncomment to generate the QR code
