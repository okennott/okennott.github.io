--[[
  Maps the compact authoring syntax in cv.qmd onto the named Word styles defined
  in design.py and carried by reference.docx.

      ## EDUCATION                     -> CVSection (bronze, ruled)

      ::: {.entry date="2018 – 2022"}
      PhD in Zoology                   -> CVEntry, with the date in the gutter
      *UCAS · Beijing, China*          -> CVMeta   (a paragraph that is all italic)
      Dissertation on ...              -> CVBody
      - supervised ...                 -> CVBullet
      :::

  Anything already carrying a custom-style attribute is left alone, which is how
  the generated blocks from the Python chunks pass through untouched.
]]

local function styled(blocks, name)
  return pandoc.Div(blocks, pandoc.Attr("", {}, {["custom-style"] = name}))
end

-- A tab, so the date sits in the gutter rather than being followed by a space.
local function tab()
  if FORMAT:match("docx") then
    -- A complete run, so it is valid wherever Pandoc places it. Closing and
    -- reopening the surrounding run instead breaks when the preceding inline is
    -- a styled span, which closes its own run.
    return pandoc.RawInline("openxml", "<w:r><w:tab/></w:r>")
  end
  return pandoc.Space()
end

-- True when every inline in the paragraph is wrapped in emphasis.
local function all_emph(inlines)
  local seen = false
  for _, il in ipairs(inlines) do
    if il.t == "Emph" then
      seen = true
    elseif il.t ~= "Space" and il.t ~= "SoftBreak" then
      return false
    end
  end
  return seen
end

local function unwrap_emph(inlines)
  local out = pandoc.List({})
  for _, il in ipairs(inlines) do
    if il.t == "Emph" then out:extend(il.content) else out:insert(il) end
  end
  return out
end

-- A bare []{.tab} anywhere means "advance to the next tab stop".
function Span(el)
  if el.classes:includes("tab") then return {tab()} end
end

-- Drop the title block: the name is rendered by the CVName style instead. The
-- title still has to exist in the metadata, or Quarto promotes the first heading.
function Meta(m)
  m.title = nil
  return m
end

function Header(el)
  if el.level == 2 then
    return styled({pandoc.Para(el.content)}, "CVSection")
  end
end

function Div(el)
  if el.attributes["custom-style"] then return nil end
  -- .entry heads a block with a bold title; .labelled is a plain label/value row.
  local lead = el.classes:includes("entry") and "CVEntry"
            or el.classes:includes("labelled") and "CVLabel"
  if not lead then return nil end

  local date = el.attributes["date"] or ""
  local out = pandoc.List({})
  local first = true

  for _, blk in ipairs(el.content) do
    if blk.t == "Para" or blk.t == "Plain" then
      if first then
        local head = pandoc.List({})
        if date ~= "" then
          head:insert(pandoc.Span(pandoc.Str(date), pandoc.Attr("", {}, {["custom-style"] = "CVDate"})))
          head:insert(tab())
        end
        head:extend(blk.content)
        out:insert(styled({pandoc.Para(head)}, lead))
        first = false
      elseif all_emph(blk.content) then
        out:insert(styled({pandoc.Para(unwrap_emph(blk.content))}, "CVMeta"))
      else
        out:insert(styled({pandoc.Para(blk.content)}, "CVBody"))
      end
    elseif blk.t == "BulletList" then
      for _, item in ipairs(blk.content) do
        local inlines = pandoc.List({pandoc.Str("\u{25AA}"), tab()})
        for _, sub in ipairs(item) do
          if sub.t == "Para" or sub.t == "Plain" then inlines:extend(sub.content) end
        end
        out:insert(styled({pandoc.Para(inlines)}, "CVBullet"))
      end
    else
      out:insert(blk)
    end
  end
  return out
end
