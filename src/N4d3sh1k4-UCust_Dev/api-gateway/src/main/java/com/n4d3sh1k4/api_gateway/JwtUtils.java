package com.n4d3sh1k4.api_gateway;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;

@Component
public class JwtUtils {
    private final SecretKey jwtAccessSecret;

    public JwtUtils(@Value("${jwt.secret.access}") String jwtAccessSecret) {
        this.jwtAccessSecret = Keys.hmacShaKeyFor(Decoders.BASE64.decode(jwtAccessSecret));
    }

    public Claims getAccessClaims(String token) {
        return Jwts.parser()
                .verifyWith(jwtAccessSecret)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public boolean validateAccessToken(String token) {
        try {
            Jwts.parser().verifyWith(jwtAccessSecret).build().parseSignedClaims(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}