<!--
This xslt stylesheet transforms (JUnit) xunit xml output to xunit.net xml, which
is eg. used at AppVeyor CI.

See for reference:
https://xunit.codeplex.com/wikipage?title=XmlFormat

tested with saxon and xsltproc against output of nosetests &#8211;&#8211; with-xml (Python)

Author: Martin Scherer <m.scherer@fu-berlin.de>
-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes" />

<!-- xunit.net handles failures and errors the same -->
  <xsl:template match="failure|error">
    <xsl:attribute name="exception-type">
        <xsl:value-of select="@type" />
    </xsl:attribute>
    <message>
      <xsl:value-of select="@message" />
    </message>
    <stack-trace>
      <xsl:value-of select="." />
    </stack-trace>
  </xsl:template>
  
  <!-- use classnames as key -->
  <xsl:key name="class" match="/testsuite/testcase/@classname"
    use="." />
  <xsl:template match="testsuite">
    <assembly name="python">
      <xsl:attribute name="total">
        <xsl:value-of select="@tests" />
      </xsl:attribute>
      <xsl:attribute name="passed">
        <xsl:value-of select="@tests - @errors - @failures - @skip" />
      </xsl:attribute>
      <xsl:attribute name="failed">
        <xsl:value-of select="@errors" />
      </xsl:attribute>
      <xsl:attribute name="skipped">
        <xsl:value-of select="@skip" />
      </xsl:attribute>

<!-- class names, only unique -->
      <xsl:for-each
        select="/testsuite/testcase/@classname[generate-id()
                                       = generate-id(key('class',.)[1])]">
        <class>
          <xsl:variable name="className" select="." />
          <xsl:attribute name="name">
            <xsl:value-of select="." />
          </xsl:attribute>
    
    <!-- select only those testcases, which match the current classname -->
          <xsl:for-each select="/testsuite/testcase[@classname=$className]">
            <test>
              <xsl:attribute name="name">
                <xsl:value-of select="concat($className, '.', @name)" />
            </xsl:attribute>
              <xsl:attribute name="time">
                <xsl:value-of select="@time" />
            </xsl:attribute>
              <xsl:variable name="result">
                <xsl:choose>
                  <xsl:when test="error or failure">Fail</xsl:when>
                  <xsl:when test="skipped">Skip</xsl:when>
                  <xsl:otherwise>Pass</xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <xsl:attribute name="result">
                <xsl:value-of select="$result" />
            </xsl:attribute>
              <xsl:choose>
                <xsl:when test="error or failure">
                  <failure>
                    <xsl:apply-templates />
                  </failure>
                </xsl:when>
                <xsl:when test="skipped">
                  <reason>
                    <xsl:value-of select="skipped/@message" />
                  </reason>
                </xsl:when>
              </xsl:choose>
              <xsl:choose>
                <xsl:when test="system-out">
                  <output>
                    <xsl:value-of select="system-out/." />
                  </output>
                </xsl:when>
              </xsl:choose>
            </test>
          </xsl:for-each>
        </class>
      </xsl:for-each>
    </assembly>
  </xsl:template>
</xsl:stylesheet>
